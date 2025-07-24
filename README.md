# AWS & OpenAI Image Extraction Demo

Diese Demo automatisiert die Analyse und Informations-Extraktion aus Bildern mithilfe von AWS Lambda, OpenAI und Amazon S3.

## Architektur

- **Amazon S3**: Speicherung der Bilder, Ergebnisse und der kleinen Weboberfläche
- **AWS Lambda**: Bildverarbeitung und API-Endpunkt
- **API Gateway**: HTTP-API für Upload und Ergebnisausgabe
- **OpenAI API**: Bildanalyse und Informations-Extraktion
- **AWS Secrets Manager**: Sicherer Speicher für den OpenAI API Key

## Deployment

1. AWS CLI konfigurieren
2. OpenAI API Key beim Ausführen des Skripts angeben und Deployment starten:
   ```bash
   ./scripts/deploy.sh
   ```
   Das Skript paketiert die Lambda-Funktionen und deployed den CloudFormation-Stack.
   Nach erfolgreichem Deploy wird die API-Endpunkt-URL ausgegeben.

## Nutzung

Die minimale Weboberfläche befindet sich in `web/index.html`. Dort die Platzhalter-URL `REPLACE_WITH_API_ENDPOINT` durch die ausgegebene API-URL ersetzen und die Datei im Browser öffnen. Ein Bild kann anschließend hochgeladen werden und nach der Verarbeitung erscheint das JSON-Ergebnis auf der Seite.
