"""Support for Amazon S3 backups."""

from __future__ import annotations

import logging
import os
from typing import cast

from homeassistant.components.backup import BackupPlatform, BackupPlatformError, BackupRequest
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .api import S3Client
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(
    hass: HomeAssistant, config: ConfigType, async_register_platform: BackupPlatform, platform_config: ConfigType
) -> None:
    """Set up the backup platform."""
    _LOGGER.warning(
        "Setup via configuration.yaml is not supported. Configure using the integration UI"
    )


async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, async_register_platform: BackupPlatform
) -> None:
    """Set up Amazon S3 backup from a config entry."""
    client: S3Client = hass.data[DOMAIN][config_entry.entry_id]

    async def async_create_backup(request: BackupRequest) -> None:
        """Create backup using config entry."""
        try:
            await client.async_upload_backup(request.backup_open_stream, request.backup)
        except Exception as err:
            raise BackupPlatformError(f"Error uploading to Amazon S3: {err}") from err

    async def async_download_backup(backup_id: str) -> str:
        """Download backup using config entry."""
        try:
            return await client.async_download(backup_id)
        except Exception as err:
            raise BackupPlatformError(f"Error downloading from Amazon S3: {err}") from err

    async def async_remove_backup(backup_id: str) -> None:
        """Remove backup using config entry."""
        try:
            await client.async_delete(backup_id)
        except Exception as err:
            raise BackupPlatformError(f"Error removing from Amazon S3: {err}") from err

    async def async_list_backups() -> list:
        """List backups using config entry."""
        try:
            return await client.async_list_backups()
        except Exception as err:
            raise BackupPlatformError(f"Error listing from Amazon S3: {err}") from err

    async_register_platform(
        domain=config_entry.unique_id or config_entry.title,
        create_backup=async_create_backup,
        download_backup=async_download_backup,
        remove_backup=async_remove_backup,
        list_backups=async_list_backups,
    )
