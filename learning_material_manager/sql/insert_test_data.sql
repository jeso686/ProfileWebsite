USE learning_material_db;

INSERT IGNORE INTO roles (id, role_name) VALUES
(1, 'Student'),
(2, 'Teacher'),
(3, 'Admin');

INSERT IGNORE INTO users (id, full_name, email, role_id) VALUES
(1, 'Anna Becker', 'anna@example.com', 1),
(2, 'Lukas Meyer', 'lukas@example.com', 2),
(3, 'Sofia Klein', 'sofia@example.com', 3);

INSERT IGNORE INTO topics (id, topic_name) VALUES
(1, 'Math'),
(2, 'Physics'),
(3, 'Computer Science');

INSERT IGNORE INTO materials (id, filename, file_type, file_size, file_path, topic_id, author_id) VALUES
(1, 'algebra_notes.pdf', 'application/pdf', 245760, 'storage/materials/algebra_notes.pdf', 1, 2),
(2, 'physics_lab.docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 98304, 'storage/materials/physics_lab.docx', 2, 2),
(3, 'python_intro.txt', 'text/plain', 4096, 'storage/materials/python_intro.txt', 3, 3);

INSERT IGNORE INTO comments (id, material_id, author_id, comment_text) VALUES
(1, 1, 1, 'Das Material ist hilfreich.'),
(2, 1, 2, 'Bitte Seite 5 beachten.'),
(3, 3, 1, 'Gute Einfuehrung fuer den Start.');

INSERT IGNORE INTO tags (id, tag_name) VALUES
(1, 'exam'),
(2, 'project'),
(3, 'summary');

INSERT IGNORE INTO material_tags (material_id, tag_id) VALUES
(1, 1),
(2, 2),
(3, 3);
