USE learning_material_db;

-- 1) Aggregation: Anzahl der Materialien pro Thema
SELECT t.topic_name, COUNT(m.id) AS material_count
FROM topics t
LEFT JOIN materials m ON m.topic_id = t.id
GROUP BY t.topic_name
ORDER BY material_count DESC;

-- 2) Aggregation: Durchschnittliche Dateigroesse pro Dateityp
SELECT file_type, AVG(file_size) AS avg_file_size
FROM materials
GROUP BY file_type
ORDER BY avg_file_size DESC;

-- 3) Inner Join: Materialien mit Autor
SELECT m.id, m.filename, u.full_name AS author_name
FROM materials m
INNER JOIN users u ON u.id = m.author_id
ORDER BY m.id ASC;

-- 4) Inner Join: Materialien mit Thema
SELECT m.id, m.filename, t.topic_name
FROM materials m
INNER JOIN topics t ON t.id = m.topic_id
ORDER BY m.id ASC;

-- 5) Join mit Aggregation: Anzahl der Kommentare pro Material
SELECT m.id, m.filename, COUNT(c.id) AS comment_count
FROM materials m
LEFT JOIN comments c ON c.material_id = m.id
GROUP BY m.id, m.filename
ORDER BY comment_count DESC;

-- 6) Mehrere Inner Joins: Material mit Autor und Rolle
SELECT m.id, m.filename, u.full_name AS author_name, r.role_name
FROM materials m
INNER JOIN users u ON u.id = m.author_id
INNER JOIN roles r ON r.id = u.role_id
ORDER BY m.id ASC;

-- 7) Mehrere Inner Joins: Kommentar mit Material, Thema und Autor
SELECT c.id, c.comment_text, m.filename, t.topic_name, u.full_name AS author_name
FROM comments c
INNER JOIN materials m ON m.id = c.material_id
INNER JOIN topics t ON t.id = m.topic_id
INNER JOIN users u ON u.id = c.author_id
ORDER BY c.id ASC;
