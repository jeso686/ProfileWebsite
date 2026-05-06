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
      algebra_notes.pdf
      physics_lab.docx
      python_intro.txt
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
8. Kommentar loeschen
9. Sieben Standard-SQL-Abfragen ausfuehren
10. Programm beenden

## Wichtiger Hinweis
Die Anwendung speichert keine Dateien in MySQL.
Beim Upload wird eine vorhandene Datei nach `storage/materials/` kopiert.
Wenn der eingegebene Pfad nicht existiert, kann direkt im Programm eine neue Textdatei mit Inhalt angelegt werden.
In MySQL werden nur Dateiname, Dateityp, Dateigroesse und Dateipfad gespeichert.
