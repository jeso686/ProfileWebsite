# Redragon .mac Generator (Offline)

Офлайн веб-приложение для генерации `.mac` (JSON) из короткого DSL-скрипта.
Открывается напрямую как `index.html`, без сборки и без сети.

## 1) Как получить `sample.mac` из Redragon
1. Откройте Redragon Software.
2. Создайте/выберите любой макрос.
3. Экспортируйте макрос в файл `.mac`.
4. Загрузите его в поле **sample.mac (required)**.

> `sample.mac` обязателен: приложение копирует структуру и поля (`Version`, `Type`, и т.д.) именно из него.

## 2) Как подготовить `mapping.json`
Формат:

```json
{
  "A": 4,
  "B": 5,
  "ENTER": 40,
  "SHIFT": 225
}
```

- Ключ: `KEY_NAME`
- Значение: `ButtonCode` (int)

Если mapping пока нет, нажмите **Download mapping template**.

## 3) Как сгенерировать и импортировать `.mac`
1. Откройте `index.html`.
2. Загрузите `sample.mac` и (желательно) `mapping.json`.
3. Введите скрипт в **Macro script**.
4. Нажмите **Generate** (или `Ctrl+Enter`).
5. Нажмите **Download .mac** (или `Ctrl+S`).
6. Импортируйте файл в Redragon Software и назначьте в профиль устройства.

## DSL
- Обычный текст: печать символов (US).
- Команды:
  - `{DELAY:ms}`
  - `{ENTER}` `{TAB}` `{SPACE}` `{BACKSPACE}` `{ESC}`
  - `{RAW:KEY}`
  - `{CHORD:CTRL+V}`
  - `{DOWN:KEY}` / `{UP:KEY}`
  - `{HOLD:KEY:ms}`
  - `{REPEAT:n} ... {/REPEAT}`
  - `{TEXT:"..."}` с `\"` и `\n`
- Экранирование: `\{` и `\\`
- Комментарий: строка, начинающаяся с `#`

## Важно по US Shift
- `:` генерируется только как `SHIFT + SEMICOLON`.
- `;` генерируется как `SEMICOLON` без Shift.
- Для символов с Shift: `SHIFT down` -> `key down/up` -> `SHIFT up`.

## Hotkeys
- `Ctrl+Enter` — Generate
- `Ctrl+S` — Download .mac
- `Ctrl+L` — Clear
- `Ctrl+/` — вставить шаблон команды
