"""The Amazon S3 Backup integration."""

from __future__ import annotations

from collections.abc import Callable

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import instance_id
from homeassistant.util.hass_dict import HassKey

from .api import S3Client
from .const import (
    CONF_AWS_ACCESS_KEY_ID,
    CONF_AWS_SECRET_ACCESS_KEY,
    CONF_BUCKET_NAME,
    CONF_BUCKET_PATH,
    CONF_REGION_NAME,
    DOMAIN,
)

DATA_BACKUP_AGENT_LISTENERS: HassKey[list[Callable[[], None]]] = HassKey(
    f"{DOMAIN}.backup_agent_listeners"
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Amazon S3 Backup from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Get credentials from config entry
    aws_access_key_id = entry.data[CONF_AWS_ACCESS_KEY_ID]
    aws_secret_access_key = entry.data[CONF_AWS_SECRET_ACCESS_KEY]
    bucket_name = entry.data[CONF_BUCKET_NAME]
    bucket_path = entry.data.get(CONF_BUCKET_PATH)
    region_name = entry.data[CONF_REGION_NAME]

    # Create S3 client
    client = S3Client(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name,
        bucket_name=bucket_name,
        bucket_path=bucket_path,
        ha_instance_id=await instance_id.async_get(hass),
    )

    # Test S3 connection and bucket access
    try:
        await hass.async_add_executor_job(client.validate_bucket_access)
    except (ClientError, NoCredentialsError) as err:
        raise ConfigEntryNotReady(f"Error connecting to Amazon S3: {err}") from err

    hass.data[DOMAIN][entry.entry_id] = client

    def async_notify_backup_listeners() -> None:
        for listener in hass.data.get(DATA_BACKUP_AGENT_LISTENERS, []):
            listener()

    entry.async_on_unload(entry.async_on_state_change(async_notify_backup_listeners))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if hass.data[DOMAIN].get(entry.entry_id):
        hass.data[DOMAIN].pop(entry.entry_id)
    return True
