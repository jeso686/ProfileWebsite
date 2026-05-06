from __future__ import annotations

from typing import Any

from app.database import execute_query, execute_transaction, fetch_all


# Fuegt einen Metadatensatz fuer eine gespeicherte Materialdatei ein.
MATERIAL_INSERT_QUERY = """
INSERT INTO materials (filename, file_type, file_size, file_path, topic_id, author_id)
VALUES (%s, %s, %s, %s, %s, %s)
"""


# Zeigt Materialien mit lesbaren Themen- und Autorennamen an.
MATERIAL_LIST_QUERY = """
SELECT m.id, m.filename, m.file_type, m.file_size, m.file_path,
       t.topic_name, u.full_name AS author_name, m.created_at
FROM materials m
INNER JOIN topics t ON t.id = m.topic_id
INNER JOIN users u ON u.id = m.author_id
ORDER BY m.id ASC
"""


# Einfache Abfragen fuer Auswahllisten im Menue.
TOPIC_LIST_QUERY = "SELECT id, topic_name FROM topics ORDER BY id"
USER_LIST_QUERY = "SELECT id, full_name FROM users ORDER BY id"


# Entfernt zuerst abhaengige Zeilen und danach das Material.
MATERIAL_DELETE_QUERIES = [
    "DELETE FROM comments WHERE material_id = %s",
    "DELETE FROM material_tags WHERE material_id = %s",
    "DELETE FROM materials WHERE id = %s",
]


def create_material(metadata: dict[str, Any], topic_id: int, author_id: int) -> int:
    # Speichert nur Metadaten und Dateipfad, niemals den Dateiinhalt.
    return execute_query(
        MATERIAL_INSERT_QUERY,
        (
            metadata["filename"],
            metadata["file_type"],
            metadata["file_size"],
            metadata["file_path"],
            topic_id,
            author_id,
        ),
    )


def list_materials() -> list[dict[str, Any]]:
    # Gibt alle Materialien fuer die Anzeige im Konsolenmenue zurueck.
    return fetch_all(MATERIAL_LIST_QUERY)


def list_topics() -> list[dict[str, Any]]:
    # Gibt Themen zurueck, damit eine Thema-ID gewaehlt werden kann.
    return fetch_all(TOPIC_LIST_QUERY)


def list_users() -> list[dict[str, Any]]:
    # Gibt Benutzer zurueck, damit eine Autor-ID gewaehlt werden kann.
    return fetch_all(USER_LIST_QUERY)


def get_material_by_id(material_id: int) -> dict[str, Any] | None:
    # Sucht ein Material, bevor es geoeffnet oder geloescht wird.
    query = "SELECT id, filename, file_path FROM materials WHERE id = %s"
    rows = fetch_all(query, (material_id,))
    return rows[0] if rows else None


def delete_material(material_id: int) -> int:
    # Loescht Kommentare, Tag-Verknuepfungen und das Material in einer Transaktion.
    query_params = [(query, (material_id,)) for query in MATERIAL_DELETE_QUERIES]
    row_counts = execute_transaction(query_params)
    return row_counts[-1]
