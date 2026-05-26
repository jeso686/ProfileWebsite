USE learning_material_db;

INSERT IGNORE INTO roles (id, role_name) VALUES
(1, 'Student'),
(2, 'Teacher'),
(3, 'Admin');

INSERT IGNORE INTO users (id, full_name, email, role_id) VALUES
(1, 'Mara Schneider', 'mara.schneider@example.com', 1),
(2, 'Nico Hartmann', 'nico.hartmann@example.com', 1),
(3, 'Lea Winter', 'lea.winter@example.com', 1),
(4, 'Pascal Fleddermann', 'pascal.fleddermann@example.com', 2),
(5, 'Jonas Reuter', 'jonas.reuter@example.com', 2),
(6, 'Hannah Vogt', 'hannah.vogt@example.com', 2),
(7, 'Sofia Klein', 'sofia.klein@example.com', 3);

INSERT IGNORE INTO topics (id, topic_name) VALUES
(1, 'Math'),
(2, 'Physics'),
(3, 'Computer Science');

INSERT IGNORE INTO materials (id, filename, file_type, file_size, file_path, topic_id, author_id) VALUES
(1, 'algebra_notes.pdf', 'application/pdf', 245760, 'storage/materials/algebra_notes.pdf', 1, 4),
(2, 'physics_lab.docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 98304, 'storage/materials/physics_lab.docx', 2, 5),
(3, 'python_intro.txt', 'text/plain', 4096, 'storage/materials/python_intro.txt', 3, 6);

INSERT IGNORE INTO comments (id, material_id, author_id, comment_text) VALUES
(1, 1, 1, 'Das Material ist hilfreich.'),
(2, 1, 4, 'Bitte Seite 5 beachten.'),
(3, 3, 2, 'Gute Einfuehrung fuer den Start.');

INSERT IGNORE INTO tags (id, tag_name) VALUES
(1, 'exam'),
(2, 'project'),
(3, 'summary');

INSERT IGNORE INTO material_tags (material_id, tag_id) VALUES
(1, 1),
(2, 2),
(3, 3);
