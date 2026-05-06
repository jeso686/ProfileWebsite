# ERM - Lernmaterialverwaltung

## Entitaeten
- `roles` (1:n) `users`
- `users` (1:n) `materials`
- `topics` (1:n) `materials`
- `materials` (1:n) `comments`
- `users` (1:n) `comments`
- `materials` (n:m) `tags` ueber `material_tags`

## Wichtige Attribute
- `materials`: filename, file_type, file_size, file_path
- `comments`: comment_text

## Hinweis
Die eigentliche Datei liegt im Dateisystem.
Die Datenbank speichert nur Metadaten und Pfad.
