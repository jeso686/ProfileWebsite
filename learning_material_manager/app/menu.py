from __future__ import annotations

import os
import platform
import subprocess

from app.comment_service import create_comment, delete_comment, list_comments_by_material
from app.database import fetch_all
from app.file_storage import (
    copy_material_to_storage,
    create_material_file,
    delete_material_file,
    file_exists,
    resolve_material_path,
)
from app.material_service import (
    add_material_tag,
    create_material,
    delete_material,
    get_material_by_id,
    list_materials,
    list_tags,
    list_topics,
    list_users_by_role,
)
from app.search_service import search_materials_by_filename, search_materials_by_topic


# Das Menue kann diese sieben SQL-Beispielabfragen fuer die Praesentation ausfuehren.
STANDARD_SQL_QUERIES = {
    1: ("Aggregation: Anzahl der Materialien pro Thema", """SELECT t.topic_name, COUNT(m.id) AS material_count FROM topics t LEFT JOIN materials m ON m.topic_id = t.id GROUP BY t.topic_name ORDER BY material_count DESC;"""),
    2: ("Aggregation: Durchschnittliche Dateigroesse pro Dateityp", """SELECT file_type, AVG(file_size) AS avg_file_size FROM materials GROUP BY file_type ORDER BY avg_file_size DESC;"""),
    3: ("Inner Join: Materialien mit Autor", """SELECT m.id, m.filename, u.full_name AS author_name FROM materials m INNER JOIN users u ON u.id = m.author_id ORDER BY m.id ASC;"""),
    4: ("Inner Join: Materialien mit Thema", """SELECT m.id, m.filename, t.topic_name FROM materials m INNER JOIN topics t ON t.id = m.topic_id ORDER BY m.id ASC;"""),
    5: ("Join mit Aggregation: Anzahl der Kommentare pro Material", """SELECT m.id, m.filename, COUNT(c.id) AS comment_count FROM materials m LEFT JOIN comments c ON c.material_id = m.id GROUP BY m.id, m.filename ORDER BY comment_count DESC;"""),
    6: ("Mehrere Inner Joins: Material mit Autor und Rolle", """SELECT m.id, m.filename, u.full_name AS author_name, r.role_name FROM materials m INNER JOIN users u ON u.id = m.author_id INNER JOIN roles r ON r.id = u.role_id ORDER BY m.id ASC;"""),
    7: ("Mehrere Inner Joins: Kommentar mit Material, Thema und Autor", """SELECT c.id, c.comment_text, m.filename, t.topic_name, u.full_name AS author_name FROM comments c INNER JOIN materials m ON m.id = c.material_id INNER JOIN topics t ON t.id = m.topic_id INNER JOIN users u ON u.id = c.author_id ORDER BY c.id ASC;"""),
}

CURRENT_USER_ID: int | None = None
CURRENT_ROLE: str | None = None


def print_table(rows: list[dict]) -> None:
    # Gibt Datenbankzeilen in einem einfachen Tabellenformat aus.
    if not rows:
        print("Keine Daten gefunden.")
        return
    headers = list(rows[0].keys())
    print(" | ".join(headers))
    print("-" * 100)
    for row in rows:
        print(" | ".join(str(row[h]) for h in headers))


def login_user() -> bool:
    # Fragt Rolle und Benutzer ab, bevor das Menue startet.
    global CURRENT_USER_ID, CURRENT_ROLE
    role_map = {"1": "admin", "2": "teacher", "3": "student"}
    while True:
        print("\n===== Anmeldung =====")
        print("1. Admin")
        print("2. Teacher")
        print("3. Student")
        print("0. Programm beenden")
        role_choice = input("Rolle waehlen: ").strip()

        if role_choice == "0":
            return False

        role_name = role_map.get(role_choice)
        if not role_name:
            print("Ungueltige Eingabe.")
            continue

        users = list_users_by_role(role_name)
        if not users:
            print("Keine Benutzer fuer diese Rolle gefunden.")
            continue

        print("\nVerfuegbare Benutzer:")
        print_table(users)
        user_id = int(input("Benutzer-ID eingeben: ").strip())
        if any(row["id"] == user_id for row in users):
            CURRENT_USER_ID = user_id
            CURRENT_ROLE = role_name
            print(f"Erfolgreich angemeldet als {role_name}.")
            return True
        print("Ungueltige Benutzer-ID fuer diese Rolle.")


def logout_user() -> None:
    # Meldet den aktuellen Benutzer ab.
    global CURRENT_USER_ID, CURRENT_ROLE
    CURRENT_USER_ID = None
    CURRENT_ROLE = None


def can_delete() -> bool:
    # Student darf keine Loeschfunktionen ausfuehren.
    return CURRENT_ROLE in {"admin", "teacher"}


def show_menu() -> None:
    # Gibt alle verfuegbaren Konsolenaktionen auf Deutsch aus.
    print("\n===== Lernmaterialverwaltung =====")
    print("1. Material hochladen")
    print("2. Alle Materialien anzeigen")
    print("3. Material nach Dateiname suchen")
    print("4. Material nach Thema suchen")
    print("5. Material oeffnen")
    print("6. Kommentar hinzufuegen")
    print("7. Kommentare anzeigen")
    if can_delete():
        print("8. Kommentar loeschen")
        print("9. Material loeschen")
    print("10. Sieben Standard-SQL-Abfragen ausfuehren")
    print("11. Programm beenden")
    print("12. Abmelden")


def select_topic() -> int:
    # Zeigt Themen an und fragt nach einer Thema-ID.
    print("\nVerfuegbare Themen:")
    topics = list_topics()
    print_table(topics)
    return int(input("Thema-ID eingeben: ").strip())


def select_tag() -> int:
    # Fragt beim Upload verpflichtend einen Tag ab.
    print("\nVerfuegbare Tags:")
    tags = list_tags()
    print_table(tags)
    return int(input("Tag-ID eingeben (EXAM/PROJECT/SUMMARY): ").strip())


def read_new_file_content() -> str:
    # Fragt Textinhalt ab, wenn keine Quelldatei gefunden wurde.
    print("Datei wurde nicht gefunden.")
    print("Es kann jetzt eine neue Datei im Speicher angelegt werden.")
    create_choice = input("Neue Datei anlegen? (j/n): ").strip().lower()
    if create_choice != "j":
        return ""
    print("Inhalt eingeben. Eine einzelne Zeile mit ENDE beendet die Eingabe.")
    lines = []
    while True:
        line = input()
        if line == "ENDE":
            break
        lines.append(line)
    return "\n".join(lines) + "\n"


def upload_material() -> None:
    # Speichert eine kopierte Datei oder erstellt eine neue Textdatei und speichert Metadaten.
    source_file_path = input("Dateipfad oder neuer Dateiname eingeben: ").strip()
    if not source_file_path:
        print("Eingabe darf nicht leer sein.")
        return
    if file_exists(source_file_path):
        metadata = copy_material_to_storage(source_file_path)
    else:
        content = read_new_file_content()
        if not content:
            print("Upload wurde abgebrochen.")
            return
        metadata = create_material_file(source_file_path, content)

    topic_id = select_topic()
    tag_id = select_tag()
    material_id = create_material(metadata, topic_id, int(CURRENT_USER_ID))
    add_material_tag(material_id, tag_id)
    print(f"Material wurde gespeichert. Neue ID: {material_id}")


def show_all_materials() -> None:
    # Laedt alle Materialien und gibt sie aus.
    print_table(list_materials())


def search_by_filename() -> None:
    # Sucht Materialien mit einer LIKE-Abfrage nach Dateiname.
    text = input("Suchtext fuer Dateiname eingeben: ").strip()
    print_table(search_materials_by_filename(text))


def search_by_topic() -> None:
    # Sucht Materialien mit einer LIKE-Abfrage nach Thema.
    text = input("Suchtext fuer Thema eingeben: ").strip()
    print_table(search_materials_by_topic(text))


def open_material() -> None:
    # Zeigt zuerst Materialien an, damit die richtige ID gewaehlt werden kann.
    print("\nVerfuegbare Materialien:")
    print_table(list_materials())
    material_id = int(input("Material-ID eingeben: ").strip())
    material = get_material_by_id(material_id)
    if not material:
        print("Material wurde nicht gefunden.")
        return
    file_path = resolve_material_path(material["file_path"])
    if not file_path.exists():
        print(f"Datei existiert nicht im Dateisystem: {file_path}")
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
    # Speichert einen neuen Kommentar fuer ein Material.
    material_id = int(input("Material-ID eingeben: ").strip())
    comment_text = input("Kommentar eingeben: ").strip()
    if not comment_text:
        print("Kommentar darf nicht leer sein.")
        return
    comment_id = create_comment(material_id, int(CURRENT_USER_ID), comment_text)
    print(f"Kommentar wurde gespeichert. Neue ID: {comment_id}")


def show_comments() -> None:
    # Zeigt alle Kommentare fuer ein ausgewaehltes Material.
    material_id = int(input("Material-ID eingeben: ").strip())
    print_table(list_comments_by_material(material_id))


def remove_comment() -> None:
    # Loescht einen ausgewaehlten Kommentar nach Bestaetigung.
    if not can_delete():
        print("Diese Funktion ist fuer Student nicht erlaubt.")
        return
    material_id = int(input("Material-ID eingeben: ").strip())
    rows = list_comments_by_material(material_id)
    print_table(rows)
    if not rows:
        return
    comment_id = int(input("Kommentar-ID zum Loeschen eingeben: ").strip())
    confirm = input("Kommentar wirklich loeschen? (j/n): ").strip().lower()
    if confirm != "j":
        print("Loeschen wurde abgebrochen.")
        return
    deleted_rows = delete_comment(comment_id, material_id)
    print("Kommentar wurde geloescht." if deleted_rows else "Kommentar wurde nicht gefunden.")


def remove_material() -> None:
    # Loescht ein Material aus der Datenbank und entfernt die gespeicherte Datei.
    if not can_delete():
        print("Diese Funktion ist fuer Student nicht erlaubt.")
        return
    print("\nVerfuegbare Materialien:")
    print_table(list_materials())
    material_id = int(input("Material-ID zum Loeschen eingeben: ").strip())
    material = get_material_by_id(material_id)
    if not material:
        print("Material wurde nicht gefunden.")
        return
    confirm = input("Material wirklich aus Datenbank und Ordner loeschen? (j/n): ").strip().lower()
    if confirm != "j":
        print("Loeschen wurde abgebrochen.")
        return
    deleted_rows = delete_material(material_id)
    if deleted_rows == 0:
        print("Material wurde nicht in der Datenbank geloescht.")
        return
    file_deleted = delete_material_file(material["file_path"])
    print("Material wurde in der Datenbank und im Ordner geloescht." if file_deleted else "Material wurde in der Datenbank geloescht. Datei war im Ordner nicht vorhanden.")


def run_standard_queries() -> None:
    # Fuehrt jede vorbereitete SQL-Abfrage aus und gibt das Ergebnis aus.
    for key, (label, query) in STANDARD_SQL_QUERIES.items():
        print(f"\n[{key}] {label}")
        print_table(fetch_all(query))


def run_menu_loop() -> None:
    # Steuert Anmeldung, Abmeldung und die Menueausfuehrung.
    while True:
        if not login_user():
            print("Programm wird beendet.")
            break

        actions = {
            "1": upload_material,
            "2": show_all_materials,
            "3": search_by_filename,
            "4": search_by_topic,
            "5": open_material,
            "6": add_comment,
            "7": show_comments,
            "8": remove_comment,
            "9": remove_material,
            "10": run_standard_queries,
        }

        while True:
            show_menu()
            choice = input("Bitte eine Option waehlen: ").strip()
            if choice == "11":
                print("Programm wird beendet.")
                return
            if choice == "12":
                logout_user()
                print("Erfolgreich abgemeldet.")
                break
            if not can_delete() and choice in {"8", "9"}:
                print("Diese Funktion ist fuer Student nicht erlaubt.")
                continue
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
