# Lernmaterialverwaltung

Einfaches Schulprojekt fuer die Systemintegration-Version.

## Rahmenbedingungen
- Python 3.11
- MySQL
- Keine GUI
- Konsolenmenue auf Deutsch
- Dateien nur im Dateisystem
- In der Datenbank nur Metadaten und Dateipfad

## Projektstruktur
```text
learning_material_manager/
  app/
    main.py
    database.py
    menu.py
    file_storage.py
    material_service.py
    comment_service.py
    search_service.py
  sql/
    create_database.sql
    create_tables.sql
    insert_test_data.sql
    standard_queries.sql
  storage/
    materials/
  docs/
    Projektdokumentation.md
    ERM.md
    Normalisierung.md
    Bedienungsanleitung.md
    Reflexion.md
  requirements.txt
  .env.example
  README.md
```

## Installation
1. Python 3.11 verwenden.
2. Abhaengigkeiten installieren:
   ```bash
   pip install -r requirements.txt
   ```
3. Konfiguration erstellen:
   ```bash
   cp .env.example .env
   ```
4. Datenbank vorbereiten:
   - `sql/create_database.sql`
   - `sql/create_tables.sql`
   - `sql/insert_test_data.sql`

## Start
```bash
cd learning_material_manager
python -m app.main
```

## Menuefunktionen
1. Material hochladen
2. Alle Materialien anzeigen
3. Material nach Dateiname suchen
4. Material nach Thema suchen
5. Material oeffnen
6. Kommentar hinzufuegen
7. Kommentare anzeigen
8. Sieben Standard-SQL-Abfragen ausfuehren
9. Programm beenden

## Wichtiger Hinweis
Die Anwendung speichert keine Dateien in MySQL.
Beim Upload wird die Datei nach `storage/materials/` kopiert.
In MySQL werden nur Dateiname, Dateityp, Dateigroesse und Dateipfad gespeichert.
