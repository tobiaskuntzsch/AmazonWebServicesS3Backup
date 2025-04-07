# Amazon S3 Backup für Home Assistant

Eine benutzerdefinierte Home Assistant Integration, die es ermöglicht, Ihre Home Assistant Backups automatisch in Amazon S3 zu speichern. Diese Integration ist kompatibel mit den neuen Home Assistant 2025 Versionen.

## Funktionen

- Einfache Einrichtung über die Home Assistant UI
- Sichere Speicherung von Backups in Amazon S3
- Vollständige Integration mit dem Home Assistant Backup-System
- Automatische Auflistung vorhandener Backups
- Möglichkeit, Backups wiederherzustellen oder zu löschen

## Voraussetzungen

- Ein Amazon Web Services (AWS) Konto
- Ein S3 Bucket für die Backups
- AWS Access Key ID und Secret Access Key mit Berechtigungen für den S3 Bucket

## Installation

### Über HACS (empfohlen)

1. Stellen Sie sicher, dass [HACS](https://hacs.xyz/) in Ihrem Home Assistant installiert ist
2. Klicken Sie auf "HACS" im Seitenmenü
3. Klicken Sie auf "Integrationen"
4. Klicken Sie auf die drei Punkte in der oberen rechten Ecke und wählen Sie "Benutzerdefinierte Repositories"
5. Fügen Sie die URL `https://github.com/tobiaskuntzsch/AmazonWebServicesS3Backup.git` hinzu und wählen Sie die Kategorie "Integration"
6. Suchen Sie nach "Amazon S3 Backup" und installieren Sie es
7. Starten Sie Home Assistant neu

### Manuelle Installation

1. Laden Sie die neueste Version dieses Repositories herunter
2. Extrahieren Sie den Inhalt
3. Kopieren Sie den Ordner `custom_components/amazon_s3_backup` in Ihren `custom_components` Ordner in Home Assistant
4. Starten Sie Home Assistant neu

## Konfiguration

Nach der Installation können Sie die Integration über die Home Assistant UI einrichten:

1. Gehen Sie zu Einstellungen > Geräte & Dienste
2. Klicken Sie auf "Integration hinzufügen"
3. Suchen Sie nach "Amazon S3 Backup"
4. Folgen Sie dem Konfigurationsassistenten:
   - Geben Sie einen Namen für die Integration ein
   - Fügen Sie Ihre AWS Access Key ID und Secret Access Key ein
   - Wählen Sie die AWS Region aus
   - Wählen Sie den S3 Bucket aus und geben Sie optional einen Pfad im Bucket an

## AWS Berechtigungen

Die Integration benötigt die folgenden S3-Berechtigungen:

- `s3:ListBucket`
- `s3:GetObject`
- `s3:PutObject`
- `s3:DeleteObject`

Hier ist ein Beispiel für eine IAM-Richtlinie, die diese Berechtigungen gewährt:

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

Ersetzen Sie `BUCKET-NAME` mit dem Namen Ihres S3 Buckets.

## Verwendung

Nach der Einrichtung wird die Integration automatisch in das Home Assistant Backup-System integriert. Sie können Backups über die normale Home Assistant Backup-Oberfläche erstellen, wiederherstellen und verwalten.

## Problembehandlung

### Die Integration zeigt keine Verbindung zu AWS her

- Überprüfen Sie, ob die AWS Access Key ID und Secret Access Key korrekt sind
- Stellen Sie sicher, dass der S3 Bucket existiert und Sie die entsprechenden Berechtigungen haben
- Überprüfen Sie, ob die richtige AWS Region ausgewählt ist

### Backups werden nicht angezeigt

- Überprüfen Sie die Home Assistant Logs auf Fehler
- Stellen Sie sicher, dass die AWS-Anmeldeinformationen noch gültig sind
- Überprüfen Sie, ob der Pfad im S3 Bucket korrekt ist

## Lizenz

MIT
