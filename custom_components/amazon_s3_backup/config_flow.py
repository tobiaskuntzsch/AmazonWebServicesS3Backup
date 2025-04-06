"""Config flow for the Amazon S3 Backup integration."""

from __future__ import annotations

import logging
from typing import Any

import boto3
import voluptuous as vol
from botocore.exceptions import ClientError, NoCredentialsError

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .api import S3Client
from .const import (
    AWS_REGIONS,
    CONF_AWS_ACCESS_KEY_ID,
    CONF_AWS_SECRET_ACCESS_KEY,
    CONF_BUCKET_NAME,
    CONF_BUCKET_PATH,
    CONF_REGION_NAME,
    DEFAULT_BUCKET_PATH,
    DEFAULT_NAME,
    DEFAULT_REGION_NAME,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


async def validate_aws_credentials(
    hass: HomeAssistant, 
    aws_access_key_id: str, 
    aws_secret_access_key: str,
    region_name: str,
) -> list[str]:
    """Validate the AWS credentials by listing S3 buckets."""
    try:
        s3_client = S3Client(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
            bucket_name="",  # Not needed for validation
            bucket_path="",  # Not needed for validation
            ha_instance_id="",  # Not needed for validation
        )
        
        buckets = await hass.async_add_executor_job(s3_client.list_buckets)
        return buckets
    
    except (ClientError, NoCredentialsError) as err:
        _LOGGER.error("Error validating AWS credentials: %s", err)
        raise


class AmazonS3BackupConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Amazon S3 Backup."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._aws_access_key_id: str | None = None
        self._aws_secret_access_key: str | None = None
        self._region_name: str = DEFAULT_REGION_NAME
        self._buckets: list[str] = []

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
                    }
                ),
            )

        await self.async_set_unique_id(user_input[CONF_NAME])
        self._abort_if_unique_id_configured()

        return await self.async_step_credentials()

    async def async_step_credentials(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle AWS credentials step."""
        errors = {}

        if user_input is not None:
            self._aws_access_key_id = user_input[CONF_AWS_ACCESS_KEY_ID]
            self._aws_secret_access_key = user_input[CONF_AWS_SECRET_ACCESS_KEY]
            self._region_name = user_input[CONF_REGION_NAME]

            try:
                self._buckets = await validate_aws_credentials(
                    self.hass,
                    self._aws_access_key_id,
                    self._aws_secret_access_key,
                    self._region_name,
                )
                return await self.async_step_bucket()
            except (ClientError, NoCredentialsError):
                errors["base"] = "invalid_credentials"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="credentials",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_AWS_ACCESS_KEY_ID): str,
                    vol.Required(CONF_AWS_SECRET_ACCESS_KEY): str,
                    vol.Required(CONF_REGION_NAME, default=DEFAULT_REGION_NAME): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=AWS_REGIONS,
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    ),
                }
            ),
            errors=errors,
        )

    async def async_step_bucket(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle bucket selection step."""
        errors = {}

        if user_input is not None:
            bucket_name = user_input[CONF_BUCKET_NAME]
            bucket_path = user_input.get(CONF_BUCKET_PATH, DEFAULT_BUCKET_PATH)

            try:
                s3_client = S3Client(
                    aws_access_key_id=self._aws_access_key_id,
                    aws_secret_access_key=self._aws_secret_access_key,
                    region_name=self._region_name,
                    bucket_name=bucket_name,
                    bucket_path=bucket_path,
                    ha_instance_id="",  # Not needed for validation
                )
                
                # Validate bucket access
                await self.hass.async_add_executor_job(s3_client.validate_bucket_access)
                
                # Create config entry
                return self.async_create_entry(
                    title=self.unique_id,
                    data={
                        CONF_AWS_ACCESS_KEY_ID: self._aws_access_key_id,
                        CONF_AWS_SECRET_ACCESS_KEY: self._aws_secret_access_key,
                        CONF_REGION_NAME: self._region_name,
                        CONF_BUCKET_NAME: bucket_name,
                        CONF_BUCKET_PATH: bucket_path,
                    },
                )
                
            except (ClientError, NoCredentialsError):
                errors["base"] = "invalid_bucket"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="bucket",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_BUCKET_NAME): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=self._buckets,
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    ),
                    vol.Optional(CONF_BUCKET_PATH, default=DEFAULT_BUCKET_PATH): str,
                }
            ),
            errors=errors,
        )
