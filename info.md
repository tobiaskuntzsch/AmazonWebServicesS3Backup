# Amazon S3 Backup for Home Assistant

[![GitHub Release][releases-shield]][releases]
[![HACS Badge][hacs-shield]][hacs]
[![License][license-shield]](LICENSE)

This Home Assistant integration allows you to store your backups in Amazon S3.

*Looking for the German version? [Click here](info.de.md) / Auf der Suche nach der deutschen Version? [Hier klicken](info.de.md)*

## Features

- Secure storage of your Home Assistant backups in AWS S3
- Full integration with the Home Assistant backup system
- Easy setup through the Home Assistant UI
- Automatic listing, restoring, and deletion of backups

## Installation

1. Install the integration via HACS
2. Restart Home Assistant
3. Go to Settings > Devices & Services > Add Integration
4. Search for "Amazon S3 Backup"
5. Follow the configuration wizard

{% if not installed %}
## Installation

- Make sure [HACS](https://hacs.xyz/) is installed
- Search for "Amazon S3 Backup" in HACS
- Install the integration and restart Home Assistant
{% endif %}

***

[releases-shield]: https://img.shields.io/github/release/tobiaskuntzsch/AmazonWebServicesS3Backup.svg
[releases]: https://github.com/tobiaskuntzsch/AmazonWebServicesS3Backup/releases
[hacs-shield]: https://img.shields.io/badge/HACS-Custom-orange.svg
[hacs]: https://github.com/hacs/integration
[license-shield]: https://img.shields.io/github/license/tobiaskuntzsch/AmazonWebServicesS3Backup.svg
