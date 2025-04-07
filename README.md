# Amazon S3 Backup for Home Assistant

A custom Home Assistant integration that allows you to automatically store your Home Assistant backups in Amazon S3. This integration is compatible with the new Home Assistant 2025 versions.

*Looking for the German version? [Click here](README.de.md) / Auf der Suche nach der deutschen Version? [Hier klicken](README.de.md)*

## Features

- Easy setup through the Home Assistant UI
- Secure storage of backups in Amazon S3
- Full integration with the Home Assistant backup system
- Automatic listing of existing backups
- Ability to restore or delete backups

## Requirements

- An Amazon Web Services (AWS) account
- An S3 bucket for backups
- AWS Access Key ID and Secret Access Key with permissions for the S3 bucket

## Installation

### Via HACS (recommended)

1. Make sure [HACS](https://hacs.xyz/) is installed in your Home Assistant
2. Click on "HACS" in the sidebar
3. Click on "Integrations"
4. Click on the three dots in the upper right corner and select "Custom repositories"
5. Add the URL `https://github.com/tobiaskuntzsch/AmazonWebServicesS3Backup.git` and choose the "Integration" category
6. Search for "Amazon S3 Backup" and install it
7. Restart Home Assistant

### Manual Installation

1. Download the latest version of this repository
2. Extract the contents
3. Copy the `custom_components/amazon_s3_backup` folder to your `custom_components` folder in Home Assistant
4. Restart Home Assistant

## Configuration

After installation, you can set up the integration through the Home Assistant UI:

1. Go to Settings > Devices & Services
2. Click "Add Integration"
3. Search for "Amazon S3 Backup"
4. Follow the configuration wizard:
   - Enter a name for the integration
   - Add your AWS Access Key ID and Secret Access Key
   - Select the AWS region
   - Choose the S3 bucket and optionally specify a path within the bucket

## AWS Permissions

The integration requires the following S3 permissions:

- `s3:ListBucket`
- `s3:GetObject`
- `s3:PutObject`
- `s3:DeleteObject`

Here's an example IAM policy that grants these permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket"
      ],
      "Resource": "arn:aws:s3:::BUCKET-NAME"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::BUCKET-NAME/*"
    }
  ]
}
```

Replace `BUCKET-NAME` with the name of your S3 bucket.

## Usage

After setup, the integration is automatically integrated into the Home Assistant backup system. You can create, restore, and manage backups through the normal Home Assistant backup interface.

## Troubleshooting

### The integration doesn't connect to AWS

- Check if the AWS Access Key ID and Secret Access Key are correct
- Make sure the S3 bucket exists and you have the appropriate permissions
- Verify that the correct AWS region is selected

### Backups are not displayed

- Check the Home Assistant logs for errors
- Make sure the AWS credentials are still valid
- Verify if the path in the S3 bucket is correct

## License

MIT
