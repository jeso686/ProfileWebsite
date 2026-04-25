from __future__ import annotations

from typing import Any

from app.database import execute_query, fetch_all


MATERIAL_INSERT_QUERY = """
INSERT INTO materials (filename, file_type, file_size, file_path, topic_id, author_id)
VALUES (%s, %s, %s, %s, %s, %s)
"""


MATERIAL_LIST_QUERY = """
SELECT m.id, m.filename, m.file_type, m.file_size, m.file_path,
       t.topic_name, u.full_name AS author_name, m.created_at
FROM materials m
INNER JOIN topics t ON t.id = m.topic_id
INNER JOIN users u ON u.id = m.author_id
ORDER BY m.id ASC
"""


TOPIC_LIST_QUERY = "SELECT id, topic_name FROM topics ORDER BY id"
USER_LIST_QUERY = "SELECT id, full_name FROM users ORDER BY id"



def create_material(metadata: dict[str, Any], topic_id: int, author_id: int) -> int:
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
    return fetch_all(MATERIAL_LIST_QUERY)


def list_topics() -> list[dict[str, Any]]:
    return fetch_all(TOPIC_LIST_QUERY)


def list_users() -> list[dict[str, Any]]:
    return fetch_all(USER_LIST_QUERY)


def get_material_by_id(material_id: int) -> dict[str, Any] | None:
    query = "SELECT id, filename, file_path FROM materials WHERE id = %s"
    rows = fetch_all(query, (material_id,))
    return rows[0] if rows else None
