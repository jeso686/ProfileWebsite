# Normalisierung

## 1. Normalform
Alle Tabellen haben atomare Werte.
Keine mehrfachen Werte in einer Spalte.

## 2. Normalform
Tabellen mit zusammengesetztem Schluessel (`material_tags`) haben keine partiellen Abhaengigkeiten.
Andere Tabellen nutzen einen einfachen Primaerschluessel (`id`).

## 3. Normalform
Nicht-Schluesselattribute haengen nur vom Primaerschluessel ab.
Beispiel: In `materials` haengen Dateiname, Dateityp, Dateigroesse und Dateipfad von `materials.id` ab.

## Ergebnis
Das Schema ist fuer dieses Schulprojekt bis 3NF normalisiert.
