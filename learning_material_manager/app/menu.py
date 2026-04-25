from __future__ import annotations

import os
import platform
import subprocess
from pathlib import Path

from app.comment_service import create_comment, list_comments_by_material
from app.database import fetch_all
from app.file_storage import copy_material_to_storage, file_exists
from app.material_service import (
    create_material,
    get_material_by_id,
    list_materials,
    list_topics,
    list_users,
)
from app.search_service import search_materials_by_filename, search_materials_by_topic


STANDARD_SQL_QUERIES = {
    1: (
        "Aggregation: Anzahl der Materialien pro Thema",
        """
        SELECT t.topic_name, COUNT(m.id) AS material_count
        FROM topics t
        LEFT JOIN materials m ON m.topic_id = t.id
        GROUP BY t.topic_name
        ORDER BY material_count DESC;
        """,
    ),
    2: (
        "Aggregation: Durchschnittliche Dateigroesse pro Dateityp",
        """
        SELECT file_type, AVG(file_size) AS avg_file_size
        FROM materials
        GROUP BY file_type
        ORDER BY avg_file_size DESC;
        """,
    ),
    3: (
        "Inner Join: Materialien mit Autor",
        """
        SELECT m.id, m.filename, u.full_name AS author_name
        FROM materials m
        INNER JOIN users u ON u.id = m.author_id
        ORDER BY m.id ASC;
        """,
    ),
    4: (
        "Inner Join: Materialien mit Thema",
        """
        SELECT m.id, m.filename, t.topic_name
        FROM materials m
        INNER JOIN topics t ON t.id = m.topic_id
        ORDER BY m.id ASC;
        """,
    ),
    5: (
        "Join mit Aggregation: Anzahl der Kommentare pro Material",
        """
        SELECT m.id, m.filename, COUNT(c.id) AS comment_count
        FROM materials m
        LEFT JOIN comments c ON c.material_id = m.id
        GROUP BY m.id, m.filename
        ORDER BY comment_count DESC;
        """,
    ),
    6: (
        "Mehrere Inner Joins: Material mit Autor und Rolle",
        """
        SELECT m.id, m.filename, u.full_name AS author_name, r.role_name
        FROM materials m
        INNER JOIN users u ON u.id = m.author_id
        INNER JOIN roles r ON r.id = u.role_id
        ORDER BY m.id ASC;
        """,
    ),
    7: (
        "Mehrere Inner Joins: Kommentar mit Material, Thema und Autor",
        """
        SELECT c.id, c.comment_text, m.filename, t.topic_name, u.full_name AS author_name
        FROM comments c
        INNER JOIN materials m ON m.id = c.material_id
        INNER JOIN topics t ON t.id = m.topic_id
        INNER JOIN users u ON u.id = c.author_id
        ORDER BY c.id ASC;
        """,
    ),
}


def show_menu() -> None:
    print("\n===== Lernmaterialverwaltung =====")
    print("1. Material hochladen")
    print("2. Alle Materialien anzeigen")
    print("3. Material nach Dateiname suchen")
    print("4. Material nach Thema suchen")
    print("5. Material oeffnen")
    print("6. Kommentar hinzufuegen")
    print("7. Kommentare anzeigen")
    print("8. Sieben Standard-SQL-Abfragen ausfuehren")
    print("9. Programm beenden")


def print_table(rows: list[dict]) -> None:
    if not rows:
        print("Keine Daten gefunden.")
        return

    headers = list(rows[0].keys())
    print(" | ".join(headers))
    print("-" * 80)
    for row in rows:
        print(" | ".join(str(row[h]) for h in headers))


def select_topic() -> int:
    print("\nVerfuegbare Themen:")
    topics = list_topics()
    print_table(topics)
    return int(input("Thema-ID eingeben: ").strip())


def select_user() -> int:
    print("\nVerfuegbare Benutzer:")
    users = list_users()
    print_table(users)
    return int(input("Benutzer-ID eingeben: ").strip())


def upload_material() -> None:
    source_file_path = input("Dateipfad eingeben: ").strip()
    if not file_exists(source_file_path):
        print("Datei wurde nicht gefunden.")
        return

    topic_id = select_topic()
    author_id = select_user()

    metadata = copy_material_to_storage(source_file_path)
    material_id = create_material(metadata, topic_id, author_id)
    print(f"Material wurde gespeichert. Neue ID: {material_id}")


def show_all_materials() -> None:
    materials = list_materials()
    print_table(materials)


def search_by_filename() -> None:
    text = input("Suchtext fuer Dateiname eingeben: ").strip()
    rows = search_materials_by_filename(text)
    print_table(rows)


def search_by_topic() -> None:
    text = input("Suchtext fuer Thema eingeben: ").strip()
    rows = search_materials_by_topic(text)
    print_table(rows)


def open_material() -> None:
    material_id = int(input("Material-ID eingeben: ").strip())
    material = get_material_by_id(material_id)
    if not material:
        print("Material wurde nicht gefunden.")
        return

    file_path = Path(material["file_path"])
    if not file_path.exists():
        print("Datei existiert nicht im Dateisystem.")
        return

    system_name = platform.system().lower()
    try:
        if system_name == "windows":
            os.startfile(str(file_path))
        elif system_name == "darwin":
            subprocess.run(["open", str(file_path)], check=False)
        else:
            subprocess.run(["xdg-open", str(file_path)], check=False)
        print(f"Datei wird geoeffnet: {file_path}")
    except Exception:
        print(f"Datei kann nicht automatisch geoeffnet werden: {file_path}")


def add_comment() -> None:
    material_id = int(input("Material-ID eingeben: ").strip())
    author_id = select_user()
    comment_text = input("Kommentar eingeben: ").strip()

    if not comment_text:
        print("Kommentar darf nicht leer sein.")
        return

    comment_id = create_comment(material_id, author_id, comment_text)
    print(f"Kommentar wurde gespeichert. Neue ID: {comment_id}")


def show_comments() -> None:
    material_id = int(input("Material-ID eingeben: ").strip())
    rows = list_comments_by_material(material_id)
    print_table(rows)


def run_standard_queries() -> None:
    for key, (label, query) in STANDARD_SQL_QUERIES.items():
        print(f"\n[{key}] {label}")
        rows = fetch_all(query)
        print_table(rows)


def run_menu_loop() -> None:
    actions = {
        "1": upload_material,
        "2": show_all_materials,
        "3": search_by_filename,
        "4": search_by_topic,
        "5": open_material,
        "6": add_comment,
        "7": show_comments,
        "8": run_standard_queries,
    }

    while True:
        show_menu()
        choice = input("Bitte eine Option waehlen: ").strip()

        if choice == "9":
            print("Programm wird beendet.")
            break

        action = actions.get(choice)
        if not action:
            print("Ungueltige Eingabe.")
            continue

        try:
            action()
        except ValueError:
            print("Bitte eine gueltige Zahl eingeben.")
        except Exception as error:
            print(f"Fehler: {error}")
