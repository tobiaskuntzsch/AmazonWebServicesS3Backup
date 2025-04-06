"""Constants for the Amazon S3 Backup integration."""

from __future__ import annotations

DOMAIN = "amazon_s3_backup"
DEFAULT_NAME = "Amazon S3 Backup"

# Configuration options
CONF_AWS_ACCESS_KEY_ID = "aws_access_key_id"
CONF_AWS_SECRET_ACCESS_KEY = "aws_secret_access_key"
CONF_BUCKET_NAME = "bucket_name"
CONF_BUCKET_PATH = "bucket_path"
CONF_REGION_NAME = "region_name"

# Default values
DEFAULT_BUCKET_PATH = "homeassistant-backups/"
DEFAULT_REGION_NAME = "us-east-1"

# Supported regions
AWS_REGIONS = [
    "us-east-1",
    "us-east-2",
    "us-west-1",
    "us-west-2",
    "ca-central-1",
    "eu-central-1",
    "eu-west-1",
    "eu-west-2",
    "eu-west-3",
    "eu-north-1",
    "eu-south-1",
    "ap-northeast-1",
    "ap-northeast-2",
    "ap-northeast-3",
    "ap-southeast-1",
    "ap-southeast-2",
    "ap-south-1",
    "sa-east-1",
    "af-south-1",
    "me-south-1",
]
