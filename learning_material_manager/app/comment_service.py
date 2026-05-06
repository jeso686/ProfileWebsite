from __future__ import annotations

from typing import Any

from app.database import execute_change, execute_query, fetch_all


COMMENT_INSERT_QUERY = """
INSERT INTO comments (material_id, author_id, comment_text)
VALUES (%s, %s, %s)
"""


COMMENT_LIST_QUERY = """
SELECT c.id, c.comment_text, c.created_at, u.full_name AS author_name
FROM comments c
INNER JOIN users u ON u.id = c.author_id
WHERE c.material_id = %s
ORDER BY c.id ASC
"""


COMMENT_DELETE_QUERY = "DELETE FROM comments WHERE id = %s AND material_id = %s"



def create_comment(material_id: int, author_id: int, comment_text: str) -> int:
    return execute_query(COMMENT_INSERT_QUERY, (material_id, author_id, comment_text))


def list_comments_by_material(material_id: int) -> list[dict[str, Any]]:
    return fetch_all(COMMENT_LIST_QUERY, (material_id,))


def delete_comment(comment_id: int, material_id: int) -> int:
    return execute_change(COMMENT_DELETE_QUERY, (comment_id, material_id))
