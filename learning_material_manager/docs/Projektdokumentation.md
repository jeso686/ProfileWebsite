# Projektdokumentation - Lernmaterialverwaltung

## Ziel
Dieses Schulprojekt zeigt eine einfache Systemintegration fuer eine Lernmaterialverwaltung.
Dateien werden nur im Dateisystem gespeichert. In MySQL werden nur Metadaten und Dateipfade gespeichert.

## Umfang
- Python-Konsolenanwendung ohne GUI
- MySQL als Datenbank
- Upload, Suche, Anzeige, Kommentare und Kommentar-Loeschung
- 7 Standard-SQL-Abfragen

## Kernidee
Beim Upload wird eine vorhandene Datei aus einem beliebigen Quellpfad nach `storage/materials/` kopiert.
Wenn kein vorhandener Pfad eingegeben wird, kann eine neue Datei mit Inhalt im Speicher angelegt werden.
Danach werden Dateiname, Typ, Groesse und Pfad in der Tabelle `materials` gespeichert.

## Abgrenzung
- Keine Weboberflaeche
- Keine Benutzeranmeldung
- Keine komplexe Rechteverwaltung
