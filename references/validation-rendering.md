# Validating & rendering .mmd files

## 1. Lint (always available, stdlib only)

```bash
python3 scripts/check_mmd.py path/to/diagram.mmd
```

Exit code 0 = PASS. It checks: diagram keyword on the first meaningful line, balanced quotes and brackets per line, `subgraph`/`end` pairing, valid flowchart arrow tokens (other diagram types skipped — they have their own arrow syntax), bare `%%` comment lines, node-ID/shape reuse, tabs, emoji. Warnings don't fail the run.

## 2. VS Code

- Raw `.mmd` files: install **Mermaid Preview** (bierner) — it adds a preview editor for `.mmd` / `.mermaid` files.
- Inside Markdown: **Markdown Preview Mermaid Support** (bierner) renders fenced blocks in `.md` files, so you can also wrap the `.mmd` content in a ```` ```mermaid ```` block.
- Keep the extension (and its bundled Mermaid) updated: `@{ icon: ... }` needs Mermaid ≥ v11, `architecture-beta` needs ≥ v11.3.

## 3. Browser

Paste the file into https://mermaid.live — same engine as the VS Code preview. Best for a quick visual check of layout, colors, and icons.

## 4. CLI render — default path via the skill script (needs node; network on first run)

```bash
bash scripts/render_mmd.sh diagram.mmd [more.mmd ...]   # writes <file>.svg next to each source + icon-fallback check
```

The script renders with `mmdc` and then verifies no `@{ icon }` fell back to a
literal `?` (`grep -c '>?</tspan>'` must be 0), exiting non-zero otherwise.
If node/npx is missing it prints SKIP and exits 0 — deliver the `.mmd` only.

Raw `mmdc` for options (theme/background/scale/format):

```bash
npx @mermaid-js/mermaid-cli -i diagram.mmd -o diagram.svg            # SVG, transparent bg
npx @mermaid-js/mermaid-cli -i diagram.mmd -o diagram.svg -t dark -b '#1e1e1e'
npx @mermaid-js/mermaid-cli -i diagram.mmd -o diagram.png --scale 2 -b white
# whole multi-view set at once:
for f in diagrams/*.mmd; do npx @mermaid-js/mermaid-cli -i "$f" -o "${f%.mmd}.svg"; done
```

First run downloads a Chromium build for puppeteer — heavy but one-time.

## 5. Parse-only check with node (lighter than mmdc)

```bash
npm i mermaid jsdom
node --input-type=module -e "
import { JSDOM } from 'jsdom';
const dom = new JSDOM('<!DOCTYPE html><body></body>');
globalThis.window = dom.window; globalThis.document = dom.window.document;
globalThis.navigator = dom.window.navigator; globalThis.DOMPurify = undefined;
const mermaid = (await import('mermaid')).default;
mermaid.initialize({ startOnLoad: false });
const fs = await import('fs');
const text = fs.readFileSync(process.argv[1] ?? 'diagram.mmd', 'utf8');
try { await mermaid.parse(text); console.log('PARSE OK'); }
catch (e) { console.error('PARSE FAIL:', e.message); process.exit(1); }
" diagram.mmd
```

`mermaid.parse()` throws on syntax errors without needing a browser.

## Common errors

| Symptom | Cause | Fix |
|---|---|---|
| `Parse error on line N` | unbalanced quotes/brackets; unquoted special chars in a label | quote all labels; run `check_mmd.py` |
| `Parse error on line 1` pointing at a `%%` line | bare `%%` comment (nothing after it) — invalid in Mermaid v11 | write `%% text` on every comment line |
| `No diagram type detected` | first line is not a diagram keyword | start with `flowchart TD`, `sequenceDiagram`, … |
| Error near `end` | missing `end` for a `subgraph` | add `end` after each subgraph |
| Invalid arrow | edge token like `->` outside a valid arrow | use `-->`, `-.->`, `==>`, `<-->` … |
| Icon shows as plain text | renderer older than Mermaid v11 | update the VS Code extension / use mmdc ≥ v11 |
| Node silently reshaped | same ID defined twice with different shapes | make node IDs unique |
| Layout too wide | `TD` with long chains | switch to `flowchart LR`, or split into subgraphs / multiple files |
| Arrowheads render as boxes at connection points | the preview failed to draw the SVG edge markers (old bundled Mermaid) — the `.mmd` itself is correct | verify via mermaid.live or `mmdc` export; update the VS Code extension (built-in Mermaid in VS Code ≥ 1.121); or restyle edges: `linkStyle default stroke:#...`, or `---` for no arrowhead |
| `?` inside a node's icon box | `@{ icon }` fallback — icon pack (fetched from CDN at render time) failed to load; not a syntax error | verify the pack loads in the target renderer, or remove `@{ icon: ... }` from the `.mmd`; confirm with `grep -c '>?</tspan>' out.svg` → 0 |
