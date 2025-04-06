# Amazon S3 Backup für Home Assistant

[![GitHub Release][releases-shield]][releases]
[![HACS Badge][hacs-shield]][hacs]
[![License][license-shield]](LICENSE)

Diese Home Assistant Integration ermöglicht das Speichern von Backups in Amazon S3.

## Features

- Sichere Speicherung Ihrer Home Assistant Backups in AWS S3
- Vollständige Integration mit dem Home Assistant Backup-System
- Einfache Einrichtung über die Home Assistant UI
- Automatisches Auflisten, Wiederherstellen und Löschen von Backups

## Installation

1. Installieren Sie die Integration über HACS
2. Starten Sie Home Assistant neu
3. Gehen Sie zu Einstellungen > Geräte & Dienste > Integration hinzufügen
4. Suchen Sie nach "Amazon S3 Backup"
5. Folgen Sie dem Konfigurationsassistenten

{% if not installed %}
## Installation

- Stellen Sie sicher, dass [HACS](https://hacs.xyz/) installiert ist
- Suchen Sie in HACS nach "Amazon S3 Backup"
- Installieren Sie die Integration und starten Sie Home Assistant neu
{% endif %}

***

[releases-shield]: https://img.shields.io/github/release/tobiaskuntzsch/AmazonWebServicesS3Backup.svg
[releases]: https://github.com/tobiaskuntzsch/AmazonWebServicesS3Backup/releases
[hacs-shield]: https://img.shields.io/badge/HACS-Custom-orange.svg
[hacs]: https://github.com/hacs/integration
[license-shield]: https://img.shields.io/github/license/tobiaskuntzsch/AmazonWebServicesS3Backup.svg
