# Redragon .mac Generator (Offline)

> Note: this README is now in **English**. The previous version was in **Russian**.

Offline web app to generate Redragon `.mac` (JSON) files from a short DSL script.
Open directly as `index.html` (no build step, no CDN, no network requests).

## 1) How to export `sample.mac` from Redragon Software
1. Open Redragon Software.
2. Create or select any macro.
3. Export the macro to a `.mac` file.
4. Load it in **sample.mac (required)**.

> `sample.mac` is required because the app preserves the original JSON structure/fields (`Version`, `Type`, etc.) from that file.

## 2) How to prepare `mapping.json`
Format example:

```json
{
  "A": 4,
  "B": 5,
  "ENTER": 40,
  "SHIFT": 225
}
```

- Key: `KEY_NAME`
- Value: `ButtonCode` (integer)

If you do not have a mapping yet, click **Download mapping template**.

## 3) How to generate and import `.mac`
1. Open `index.html`.
2. Load `sample.mac` and (optionally) `mapping.json`.
3. Enter script in **Macro script**.
4. Click **Generate** (or press `Ctrl+Enter`).
5. Click **Download .mac** (or press `Ctrl+S`).
6. Import the generated file in Redragon Software and assign it to your profile/device key.

## DSL
- Plain text: type characters using US layout.
- Commands:
  - `{DELAY:ms}`
  - `{ENTER}` `{TAB}` `{SPACE}` `{BACKSPACE}` `{ESC}`
  - `{RAW:KEY}`
  - `{CHORD:CTRL+V}`
  - `{DOWN:KEY}` / `{UP:KEY}`
  - `{HOLD:KEY:ms}`
  - `{REPEAT:n} ... {/REPEAT}`
  - `{TEXT:"..."}` with `\"` and `\n`
- Escaping: `\{` and `\\`
- Comments: lines starting with `#`

## Important US Shift rules
- `:` is generated strictly as `SHIFT + SEMICOLON`.
- `;` is generated as `SEMICOLON` without Shift.
- For shifted symbols: `SHIFT down` -> `key down/up` -> `SHIFT up`.


## Redragon event Type handling
- The generator writes `Delay` as a **string** (for example `"70"`), matching Redragon exports.
- Event `Type` is routed per button category:
  - modifier buttons (`1,2,4,8,16,32,64,128`) -> modifier type (normally `9`)
  - all other buttons -> key type (normally `10`)
- If your loaded `sample.mac` does not contain both categories, the app shows a warning and uses fallback `mod=9`, `key=10` for missing category.

## Hotkeys
- `Ctrl+Enter` — Generate
- `Ctrl+S` — Download `.mac`
- `Ctrl+L` — Clear
- `Ctrl+/` — insert command template
