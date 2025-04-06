"""Backup platform for the Amazon S3 Backup integration."""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable, Coroutine
import logging
from typing import Any

from botocore.exceptions import ClientError, NoCredentialsError

from homeassistant.components.backup import (
    AgentBackup,
    BackupAgent,
    BackupAgentError,
    BackupNotFound,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import ChunkAsyncStreamIterator
from homeassistant.util import slugify

from . import DATA_BACKUP_AGENT_LISTENERS
from .api import S3Client
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_get_backup_agents(
    hass: HomeAssistant,
    **kwargs: Any,
) -> list[BackupAgent]:
    """Return a list of backup agents."""
    entries = hass.config_entries.async_loaded_entries(DOMAIN)
    return [AmazonS3BackupAgent(hass, entry) for entry in entries]


@callback
def async_register_backup_agents_listener(
    hass: HomeAssistant,
    *,
    listener: Callable[[], None],
    **kwargs: Any,
) -> Callable[[], None]:
    """Register a listener to be called when agents are added or removed.

    :return: A function to unregister the listener.
    """
    hass.data.setdefault(DATA_BACKUP_AGENT_LISTENERS, []).append(listener)

    @callback
    def remove_listener() -> None:
        """Remove the listener."""
        hass.data[DATA_BACKUP_AGENT_LISTENERS].remove(listener)
        if not hass.data[DATA_BACKUP_AGENT_LISTENERS]:
            del hass.data[DATA_BACKUP_AGENT_LISTENERS]

    return remove_listener


class AmazonS3BackupAgent(BackupAgent):
    """Amazon S3 backup agent."""

    domain = DOMAIN

    def __init__(self, hass: HomeAssistant, config_entry) -> None:
        """Initialize the Amazon S3 backup agent."""
        super().__init__()
        self.hass = hass
        self.name = config_entry.title
        self.unique_id = slugify(config_entry.entry_id)
        self._client: S3Client = hass.data[DOMAIN][config_entry.entry_id]

    async def async_upload_backup(
        self,
        *,
        open_stream: Callable[[], Coroutine[Any, Any, AsyncIterator[bytes]]],
        backup: AgentBackup,
        **kwargs: Any,
    ) -> None:
        """Upload a backup.

        :param open_stream: A function returning an async iterator that yields bytes.
        :param backup: Metadata about the backup that should be uploaded.
        """
        try:
            _LOGGER.debug("Uploading backup to Amazon S3: %s", backup.backup_id)
            await self._client.async_upload_backup(open_stream, backup)
            _LOGGER.debug("Successfully uploaded backup to Amazon S3: %s", backup.backup_id)
        except (ClientError, NoCredentialsError, HomeAssistantError, TimeoutError) as err:
            raise BackupAgentError(f"Failed to upload backup to Amazon S3: {err}") from err

    async def async_list_backups(self, **kwargs: Any) -> list[AgentBackup]:
        """List backups."""
        try:
            _LOGGER.debug("Listing backups from Amazon S3")
            backups = await self._client.async_list_backups()
            _LOGGER.debug("Retrieved %d backups from Amazon S3", len(backups))
            return backups
        except (ClientError, NoCredentialsError, HomeAssistantError, TimeoutError) as err:
            raise BackupAgentError(f"Failed to list backups from Amazon S3: {err}") from err

    async def async_get_backup(
        self,
        backup_id: str,
        **kwargs: Any,
    ) -> AgentBackup:
        """Return a backup."""
        backups = await self.async_list_backups()
        for backup in backups:
            if backup.backup_id == backup_id:
                return backup
        raise BackupNotFound(f"Backup {backup_id} not found")

    async def async_download_backup(
        self,
        backup_id: str,
        **kwargs: Any,
    ) -> str:
        """Download a backup file.

        :param backup_id: The ID of the backup that was returned in async_list_backups.
        :return: Path to the downloaded backup file.
        """
        _LOGGER.debug("Downloading backup_id: %s", backup_id)
        try:
            temp_file = await self._client.async_download(backup_id)
            _LOGGER.debug("Downloaded backup to: %s", temp_file)
            return temp_file
        except (ClientError, NoCredentialsError, HomeAssistantError, TimeoutError) as err:
            raise BackupAgentError(f"Failed to download backup from Amazon S3: {err}") from err
        except FileNotFoundError:
            raise BackupNotFound(f"Backup {backup_id} not found")

    async def async_delete_backup(
        self,
        backup_id: str,
        **kwargs: Any,
    ) -> None:
        """Delete a backup file.

        :param backup_id: The ID of the backup that was returned in async_list_backups.
        """
        _LOGGER.debug("Deleting backup_id: %s", backup_id)
        try:
            await self._client.async_delete(backup_id)
            _LOGGER.debug("Deleted backup_id: %s from Amazon S3", backup_id)
        except (ClientError, NoCredentialsError, HomeAssistantError, TimeoutError) as err:
            raise BackupAgentError(f"Failed to delete backup from Amazon S3: {err}") from err
        except FileNotFoundError:
            raise BackupNotFound(f"Backup {backup_id} not found")
