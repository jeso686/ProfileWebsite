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
8. Kommentar loeschen
9. Material loeschen
10. Standard-SQL-Abfragen ausfuehren
11. Programm beenden

## Upload-Ablauf
- Dateipfad oder neuer Dateiname eingeben
- Wenn die Datei existiert, wird sie nach `storage/materials/` kopiert
- Wenn die Datei nicht existiert, kann eine neue Datei mit Inhalt angelegt werden
- Metadaten werden in `materials` gespeichert

## Kommentar loeschen
- Material-ID eingeben
- Kommentare werden angezeigt
- Kommentar-ID eingeben
- Loeschen mit `j` bestaetigen

## Material loeschen
- Menuepunkt 9 auswaehlen
- Material-ID eingeben
- Loeschen mit `j` bestaetigen
- Der Datenbankeintrag und die Datei im Ordner werden geloescht
