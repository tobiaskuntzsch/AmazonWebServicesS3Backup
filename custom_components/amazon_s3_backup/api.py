"""API for Amazon S3 Backup."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Callable, Coroutine
from datetime import datetime
import json
import logging
import os
from typing import Any, BinaryIO

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from homeassistant.components.backup import AgentBackup, suggested_filename

_LOGGER = logging.getLogger(__name__)


class S3Client:
    """Amazon S3 client."""

    def __init__(
        self,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        region_name: str,
        bucket_name: str,
        bucket_path: str | None,
        ha_instance_id: str,
    ) -> None:
        """Initialize Amazon S3 client."""
        self._aws_access_key_id = aws_access_key_id
        self._aws_secret_access_key = aws_secret_access_key
        self._region_name = region_name
        self._bucket_name = bucket_name
        
        # Standardize bucket_path: ensure it exists, doesn't start with / but ends with /
        self._bucket_path = bucket_path.strip() if bucket_path else ""
        if self._bucket_path.startswith("/"):
            self._bucket_path = self._bucket_path[1:]
        if self._bucket_path and not self._bucket_path.endswith("/"):
            self._bucket_path += "/"
            
        _LOGGER.info("S3 bucket path configured: '%s'", self._bucket_path)
        self._ha_instance_id = ha_instance_id
        self._s3_client = None

    def _get_s3_client(self):
        """Get S3 client, creating it if necessary."""
        if self._s3_client is None:
            self._s3_client = boto3.client(
                "s3",
                aws_access_key_id=self._aws_access_key_id,
                aws_secret_access_key=self._aws_secret_access_key,
                region_name=self._region_name,
            )
        return self._s3_client

    def validate_bucket_access(self) -> bool:
        """Validate that we can access the S3 bucket."""
        s3_client = self._get_s3_client()
        # Check bucket exists and we have access
        s3_client.head_bucket(Bucket=self._bucket_name)
        return True

    def list_buckets(self) -> list[str]:
        """List available S3 buckets."""
        s3_client = self._get_s3_client()
        response = s3_client.list_buckets()
        return [bucket["Name"] for bucket in response["Buckets"]]

    def _get_metadata_key(self, backup_id: str) -> str:
        """Get the S3 key for backup metadata."""
        return f"{self._bucket_path}metadata/{backup_id}.json"

    def _get_backup_key(self, filename: str) -> str:
        """Get the S3 key for backup file."""
        return f"{self._bucket_path}{filename}"

    async def async_upload_backup(
        self,
        open_stream: Callable[[], Coroutine[Any, Any, AsyncIterator[bytes]]],
        backup: AgentBackup,
    ) -> None:
        """Upload a backup file to S3."""
        filename = suggested_filename(backup)
        backup_key = self._get_backup_key(filename)
        metadata_key = self._get_metadata_key(backup.backup_id)

        # Create a temp file to store the stream content
        temp_file_path = f"/tmp/{filename}"
        
        # Write stream to temp file
        stream = await open_stream()  # Hier wird open_stream aufgerufen und der Iterator zurückgegeben
        
        with open(temp_file_path, "wb") as temp_file:
            async for chunk in stream:  # Dann iterieren wir direkt über den Iterator
                temp_file.write(chunk)

        # Upload the backup file and metadata
        try:
            s3_client = self._get_s3_client()
            
            # Upload the backup file
            _LOGGER.debug(
                "Uploading backup %s to S3 bucket %s at key '%s'",
                backup.backup_id,
                self._bucket_name,
                backup_key,
            )
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: s3_client.upload_file(
                    temp_file_path, 
                    self._bucket_name, 
                    backup_key,
                    ExtraArgs={
                        "Metadata": {
                            "backup_id": backup.backup_id,
                            "instance_id": self._ha_instance_id,
                        }
                    }
                )
            )
            
            # Store metadata as a separate JSON file
            _LOGGER.debug(
                "Storing metadata for backup %s to S3 bucket %s at key '%s'",
                backup.backup_id,
                self._bucket_name,
                metadata_key,
            )
            metadata = json.dumps(backup.as_dict())
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: s3_client.put_object(
                    Bucket=self._bucket_name,
                    Key=metadata_key,
                    Body=metadata.encode("utf-8"),
                    ContentType="application/json",
                )
            )
            
            _LOGGER.info(
                "Successfully uploaded backup %s to S3 with key '%s'", 
                backup.backup_id,
                backup_key
            )
        finally:
            # Clean up temp file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    async def async_list_backups(self) -> list[AgentBackup]:
        """List backups in the S3 bucket."""
        backups = []
        s3_client = self._get_s3_client()
        
        # List metadata files
        metadata_prefix = f"{self._bucket_path}metadata/"
        
        _LOGGER.debug("Looking for backup metadata in '%s'", metadata_prefix)
        
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: s3_client.list_objects_v2(
                    Bucket=self._bucket_name,
                    Prefix=metadata_prefix,
                )
            )
            
            if "Contents" not in response:
                _LOGGER.info("No backup metadata found in prefix '%s'", metadata_prefix)
                return []
                
            for item in response["Contents"]:
                metadata_key = item["Key"]
                
                # Get and parse metadata file
                metadata_obj = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: s3_client.get_object(
                        Bucket=self._bucket_name,
                        Key=metadata_key,
                    )
                )
                
                metadata_content = metadata_obj["Body"].read().decode("utf-8")
                backup_data = json.loads(metadata_content)
                
                backup = AgentBackup.from_dict(backup_data)
                backups.append(backup)
                
        except (ClientError, NoCredentialsError) as err:
            _LOGGER.error("Error listing backups: %s", err)
            
        return backups

    async def async_delete(self, backup_id: str) -> None:
        """Delete a backup from S3."""
        s3_client = self._get_s3_client()
        
        # Find the backup file based on metadata
        metadata_key = self._get_metadata_key(backup_id)
        
        try:
            # First get the metadata to know the backup filename
            _LOGGER.debug("Getting metadata from '%s' to determine backup file", metadata_key)
            metadata_obj = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: s3_client.get_object(
                    Bucket=self._bucket_name,
                    Key=metadata_key,
                )
            )
            
            metadata_content = metadata_obj["Body"].read().decode("utf-8")
            backup_data = json.loads(metadata_content)
            
            # Get backup filename from metadata
            backup = AgentBackup.from_dict(backup_data)
            filename = suggested_filename(backup)
            backup_key = self._get_backup_key(filename)
            
            # Delete backup file
            _LOGGER.debug("Deleting backup file from '%s'", backup_key)
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: s3_client.delete_object(
                    Bucket=self._bucket_name,
                    Key=backup_key,
                )
            )
            
            # Delete metadata file
            _LOGGER.debug("Deleting metadata file from '%s'", metadata_key)
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: s3_client.delete_object(
                    Bucket=self._bucket_name,
                    Key=metadata_key,
                )
            )
            
            _LOGGER.info("Successfully deleted backup %s from S3", backup_id)
        except (ClientError, NoCredentialsError) as err:
            _LOGGER.error("Error deleting backup %s: %s", backup_id, err)
            raise

    async def async_download(self, backup_id: str) -> str:
        """Download a backup file from S3 and return the local path."""
        s3_client = self._get_s3_client()
        
        # Find the backup file based on metadata
        metadata_key = self._get_metadata_key(backup_id)
        
        try:
            # First get the metadata to know the backup filename
            _LOGGER.debug("Getting metadata from '%s' to determine backup file for download", metadata_key)
            metadata_obj = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: s3_client.get_object(
                    Bucket=self._bucket_name,
                    Key=metadata_key,
                )
            )
            
            metadata_content = metadata_obj["Body"].read().decode("utf-8")
            backup_data = json.loads(metadata_content)
            
            # Get backup filename from metadata
            backup = AgentBackup.from_dict(backup_data)
            filename = suggested_filename(backup)
            backup_key = self._get_backup_key(filename)
            
            # Create temp file for download
            temp_file_path = f"/tmp/{filename}"
            
            # Download backup file
            _LOGGER.debug("Downloading backup file from '%s' to '%s'", backup_key, temp_file_path)
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: s3_client.download_file(
                    self._bucket_name,
                    backup_key,
                    temp_file_path,
                )
            )
            
            _LOGGER.info(
                "Successfully downloaded backup %s from S3 to %s", 
                backup_id, 
                temp_file_path
            )
            
            return temp_file_path
        except (ClientError, NoCredentialsError) as err:
            _LOGGER.error("Error downloading backup %s: %s", backup_id, err)
            raise
