from __future__ import annotations

from typing import Any

from app.database import fetch_all


# Sucht Materialien nach Teilen des Dateinamens.
SEARCH_BY_FILENAME_QUERY = """
SELECT id, filename, file_type, file_size, file_path
FROM materials
WHERE filename LIKE %s
ORDER BY id ASC
"""


# Sucht Materialien nach Teilen des Themennamens.
SEARCH_BY_TOPIC_QUERY = """
SELECT m.id, m.filename, t.topic_name, u.full_name AS author_name, m.created_at
FROM materials m
INNER JOIN topics t ON t.id = m.topic_id
INNER JOIN users u ON u.id = m.author_id
WHERE t.topic_name LIKE %s
ORDER BY m.id ASC
"""


def search_materials_by_filename(filename_text: str) -> list[dict[str, Any]]:
    # Ergaenzt Platzhalter fuer eine flexible LIKE-Suche.
    return fetch_all(SEARCH_BY_FILENAME_QUERY, (f"%{filename_text}%",))


def search_materials_by_topic(topic_text: str) -> list[dict[str, Any]]:
    # Ergaenzt Platzhalter fuer eine flexible LIKE-Suche.
    return fetch_all(SEARCH_BY_TOPIC_QUERY, (f"%{topic_text}%",))
