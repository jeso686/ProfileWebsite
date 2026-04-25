# Bedienungsanleitung

## Start
1. Abhaengigkeiten installieren: `pip install -r requirements.txt`
2. `.env.example` nach `.env` kopieren und anpassen.
3. SQL-Skripte in MySQL ausfuehren.
4. Programm starten: `python -m app.main`

## Menuefunktionen
1. Material hochladen
2. Alle Materialien anzeigen
3. Material nach Dateiname suchen
4. Material nach Thema suchen
5. Material oeffnen
6. Kommentar hinzufuegen
7. Kommentare anzeigen
8. Standard-SQL-Abfragen ausfuehren
9. Programm beenden

## Upload-Ablauf
- Dateipfad eingeben
- Existenz wird geprueft
- Datei wird nach `storage/materials/` kopiert
- Metadaten werden in `materials` gespeichert
