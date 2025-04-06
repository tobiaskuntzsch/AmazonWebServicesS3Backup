"""Support for Amazon S3 backups."""

from __future__ import annotations

import logging
import os
from typing import cast

from homeassistant.components.backup import (
    BackupPlatform,
    BackupPlatformError,
    BackupRequest,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .api import S3Client
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities
) -> None:
    """Set up Amazon S3 backup from a config entry."""
    _LOGGER.debug("Setting up Amazon S3 backup platform")
    client: S3Client = hass.data[DOMAIN][config_entry.entry_id]

    async def async_create_backup(request: BackupRequest) -> None:
        """Create backup using config entry."""
        try:
            await client.async_upload_backup(request.backup_open_stream, request.backup)
        except Exception as err:
            _LOGGER.error("Error uploading backup to Amazon S3: %s", err)
            raise BackupPlatformError(f"Error uploading to Amazon S3: {err}") from err

    async def async_download_backup(backup_id: str) -> str:
        """Download backup using config entry."""
        try:
            return await client.async_download(backup_id)
        except Exception as err:
            _LOGGER.error("Error downloading backup from Amazon S3: %s", err)
            raise BackupPlatformError(f"Error downloading from Amazon S3: {err}") from err

    async def async_remove_backup(backup_id: str) -> None:
        """Remove backup using config entry."""
        try:
            await client.async_delete(backup_id)
        except Exception as err:
            _LOGGER.error("Error removing backup from Amazon S3: %s", err)
            raise BackupPlatformError(f"Error removing from Amazon S3: {err}") from err

    async def async_list_backups() -> list:
        """List backups using config entry."""
        try:
            return await client.async_list_backups()
        except Exception as err:
            _LOGGER.error("Error listing backups from Amazon S3: %s", err)
            raise BackupPlatformError(f"Error listing from Amazon S3: {err}") from err

    # Create the backup platform
    platform = BackupPlatform(
        domain=DOMAIN,
        name=config_entry.title,
        create_backup=async_create_backup,
        download_backup=async_download_backup,
        remove_backup=async_remove_backup,
        list_backups=async_list_backups,
    )

    # Try to register the platform directly with the backup component
    # This approach works for Home Assistant 2025
    try:
        from homeassistant.components.backup import async_register_backup_platform
        _LOGGER.info("Registering Amazon S3 backup platform using async_register_backup_platform")
        async_register_backup_platform(hass, platform)
    except ImportError:
        # Fallback for Home Assistant 2025
        _LOGGER.info("Registering Amazon S3 backup platform using internal API")
        from homeassistant.components import backup
        
        if hasattr(backup, "PLATFORMS"):
            # Try to register using direct assignment to PLATFORMS
            backup.PLATFORMS.append(platform)
            _LOGGER.info("Added platform to backup.PLATFORMS")
        elif hasattr(backup, "_platforms"):
            # Try to register using direct assignment to _platforms
            backup._platforms.append(platform)
            _LOGGER.info("Added platform to backup._platforms")
        else:
            _LOGGER.error("Could not register backup platform, unsupported Home Assistant version")
