# Presentation options for the final view

The diagrams already carry per-layer `classDef` colors. On top of that, offer the user **2–3 presentation options** when delivering (step 7 of SKILL.md). All verified against Mermaid v11.17.

## Option A — built-in theme (one-line change, matches the reader's editor)

Best when the diagram will be viewed in VS Code / GitHub with a dark or light UI.

```mermaid
---
config:
  theme: dark        # default | dark | forest | neutral | base
---
flowchart TD
```

- Directive form (works everywhere, must be a `%%{...}%%` line before the keyword): `%%{init: {'theme': 'dark'}}%%`
- CLI: `npx @mermaid-js/mermaid-cli -i architecture.mmd -o architecture-dark.svg -t dark -b '#1e1e1e'`
- mermaid.live: hamburger menu → theme. VS Code Mermaid Preview follows its own theme unless the file pins one.

## Option B — custom brand palette via `themeVariables`

Keep the per-layer `classDef`s for node fills (they win over theme colors) and set the rest — background, edges, text, fonts — from one place:

```mermaid
---
config:
  theme: base
  themeVariables:
    primaryColor: "#E3F2FD"
    primaryTextColor: "#212121"
    primaryBorderColor: "#1565C0"
    lineColor: "#455A64"
    secondaryColor: "#E8F5E9"
    fontFamily: "Inter, sans-serif"
    fontSize: "15px"
---
flowchart TD
```

Useful variables: `primaryColor`, `primaryBorderColor`, `primaryTextColor`, `lineColor`, `secondaryColor`, `tertiaryColor`, `background`, `mainBkg`, `fontFamily`, `fontSize`. Full list: https://mermaid.js.org/config/theming.html

## Option C — hand-drawn look (slide decks, informal docs)

```mermaid
---
config:
  look: handDrawn    # Mermaid >= v11.6 (legacy alias: theme: handDrawn)
---
flowchart TD
```

Sketchy borders + handwriting-style font. Requires a recent renderer (VS Code preview extension up to date, or mmdc ≥ v11.6).

## Export formats (how the final view leaves Mermaid)

| Output | Use for | Command |
|---|---|---|
| `.svg` | docs, GitHub, VS Code — vector, transparent bg by default | `mmdc -i diagram.mmd -o diagram.svg` (add `-b white` to force a background) |
| `.png` | slides, chat, issues | `mmdc -i diagram.mmd -o diagram.png --scale 2 -b white` |
| `.pdf` | print / handouts | `mmdc -i diagram.mmd -o diagram.pdf -b white` |
| interactive | sharing / live editing | paste into https://mermaid.live → Export, or copy SVG |
| in VS Code | viewing only | Mermaid Preview renders `.mmd` directly; Markdown Preview Mermaid Support renders ` ```mermaid ` blocks in `.md` |

Batch export of a multi-view set: `for f in diagrams/*.mmd; do mmdc -i "$f" -o "${f%.mmd}.svg"; done`

## Version requirements cheat sheet

| Feature | Mermaid version |
|---|---|
| `@{ icon: "fa:..." }` node icons | ≥ v11 |
| `architecture-beta` diagram | ≥ v11.3 |
| `look: handDrawn` | ≥ v11.6 |
| YAML frontmatter `config:` block | ≥ v11 (directive `%%{init}%%` works in v10 too) |

Rule of thumb: pin the theme in the file (Option A/C) when the audience is fixed; leave the file theme-free and choose at export time (`-t dark`) when the same diagram goes to both light and dark contexts.
