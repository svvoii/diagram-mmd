---
name: diagram-mmd
description: Creates Mermaid (.mmd) diagrams for code logic, system architecture, data flows, request sequences, and processes. Investigates the target codebase or system, chooses the right diagram type (flowchart, sequence, class, ER, state, gantt, ...), and writes a syntax-validated .mmd file that renders in VS Code Mermaid Preview, mermaid.live, or mmdc. Activate when the user asks for a diagram, flowchart, architecture overview, or a visual explanation of how a system or code path works.
license: MIT
compatibility: Any agent with filesystem read/write access. Optional: python3 for scripts/check_mmd.py; node + npx with network access for full render checks (see references/validation-rendering.md).
metadata:
  author: serge
  version: "1.0.0"
---

# diagram-mmd — build Mermaid (.mmd) diagrams

You turn a codebase, system, or process into a **Mermaid diagram file (`.mmd`)** that renders in VS Code (Mermaid Preview / Markdown Preview Mermaid Support), https://mermaid.live, or the `mmdc` CLI.

**Output contract:** one `.mmd` file per diagram (UTF-8, first line = diagram keyword, default `flowchart TD`), written to `<target-dir>/diagrams/` unless the user names an explicit output path, lint-validated, plus a rendered `.svg` sibling by default.

## Workflow

### 1. Clarify scope — only if it would change the result
Ask at most two short questions when the request is ambiguous. Defaults when the user does not specify:

- Diagram type: `flowchart TD` for architecture / logic / data flow. Use `sequenceDiagram` for request/response interactions over time — see [references/diagram-types.md](references/diagram-types.md).
- Output location: **`<target-dir>/diagrams/<topic>.mmd`** — always inside a `diagrams/` folder in the directory the user indicated as the target; create the folder if it doesn't exist. Examples: target = repo root → `repo/diagrams/architecture.mmd`; target = `.docs` → `.docs/diagrams/query-flow.mmd`. If the user names an explicit file path, use exactly that instead.
- Detail level: one system-overview diagram with subgraphs per layer/service. Split into multiple files only when a single diagram would exceed ~30 nodes.
- Audience: engineers — keep file names, ports, model names, and config values accurate.

### 2. Investigate the target before drawing
Read the repo/system first; never diagram from the request alone.

- Entry points: `main.py`, CLI commands, REST handlers, `docker-compose.yml`, `Dockerfile`, package manifests (`pyproject.toml`, `package.json`).
- README + docs for intent and tech stack.
- Trace **one full end-to-end path** (e.g. user question → retrieval → LLM → answer) and note every component, data store, and external service on it, with ports / models / versions.
- Extract the facts worth showing: file names, ports, model names, top_k, chunk sizes, provider lists.

If the target is a process, org, or pipeline rather than code, extract from docs and conversation instead.

### 3. Choose the diagram type
Default `flowchart TD`. Decision table + copy-paste minimal examples for every type: [references/diagram-types.md](references/diagram-types.md).

### 4. Model the diagram
- One concept per node; label ≤ ~8 words. Put detail in the edge label or a `%%` comment.
- Node IDs: short, `[A-Za-z0-9_]`, unique per file. Never reuse an ID with a different shape. Avoid reserved words: `end`, `graph`, `flowchart`, `subgraph`, `direction`, `click`, `style`, `class`, `classDef`, `linkStyle`.
- Quote **every** label: `A["text"]`. Inside quotes avoid a raw `"` — use `#quot;`. Line break inside a label: `<br/>`.
- Group boundaries with subgraphs: `subgraph ING["Ingestion pipeline"]` … `end`, optional `direction TB|LR` inside. Edges may point at a subgraph ID.
- Data stores → cylinder `[("...")]`; external services → icon + "(external)" in the label.
- Edges carry verbs: `A -- ingest --> B`; optional/async paths dotted: `A -. retry .-> B`.
- Node budget: hard limit ~30 nodes per file; aim for ~10–15 per view so each diagram stays digestible. Beyond that, split — see "Splitting a large system into multiple views" below.

### Splitting a large system into multiple views
When one diagram would exceed the budget or mix unrelated concerns (offline ingestion vs online query vs deployment vs evaluation):

- Keep one **entry-point overview** in the same `diagrams/` folder (e.g. `diagrams/architecture.mmd`) with ≤ ~10 nodes: boundaries + main flow only; side concerns (deploy, eval) as dotted edges.
- Put **detail views** as siblings in that folder, one logical part per file — e.g. `diagrams/ingestion.mmd`, `diagrams/query-flow.mmd`, `diagrams/request-sequence.mmd`, `diagrams/deployment.mmd`, `diagrams/evaluation.mmd`.
- Cross-reference views in the `%%` header comment of every file so readers can navigate between them.
- Render the whole set in one go from the target dir: `bash scripts/render_mmd.sh diagrams/*.mmd`.
- Keep node IDs stable across files when the same component appears in several views, so it can be traced.
- Use a second diagram type where it fits — e.g. `sequenceDiagram` for one request over time (see [references/diagram-types.md](references/diagram-types.md)).

### 5. Draft the diagram
Write a valid `.mmd` **from scratch** — everything needed is in this file plus [references/flowchart-syntax.md](references/flowchart-syntax.md); no starter template file is needed.

- Prefer `classDef` + `class A,B myClass` over per-node `style` lines.
- House edge style (unless the user asks otherwise): `linkStyle default stroke:#607D8B,stroke-width:1.5px` — one neutral edge color for the whole set, so colored nodes carry the visual weight. Arrowheads stay the theme's filled triangle; per-edge markers via `---` / `==>` / `o--o` / `x--x`.
- ≤ 6 classes, one per layer/subgraph; light fills with dark text (or white text on dark fill). Colorblind-safe palette.
- Icons (`@{ icon: "fa:..." }`) are optional and fragile: Mermaid ≥ v11 fetches icon packs from a CDN at render time, and when the pack can't load the icon renders as a literal `?` box. Use them only if the target renderer is verified to load the pack; otherwise rely on shapes + `classDef` colors. After any render, `grep -c '>?</tspan>' out.svg` must be 0 — details in [references/flowchart-syntax.md](references/flowchart-syntax.md).
- For the final look, offer 2–3 presentation options from [references/styling-themes.md](references/styling-themes.md): built-in theme (e.g. `dark`), custom `themeVariables` palette, hand-drawn `look`, plus SVG/PNG/PDF export.

### 6. Write, validate, and render the file
1. Save as UTF-8 `.mmd`. The diagram keyword (`flowchart TD` by default) must come before any diagram content — a `%%` header comment block may precede it, but every `%%` line must have text after it (a bare `%%` line is a parse error in Mermaid v11).
2. Header comment block at the top: title, target repo, the sibling SVG name, how to render.
3. Lint: `python3 <skill-dir>/scripts/check_mmd.py <file>` — must report PASS (warnings OK, but read them: W5 = icon may render as `?`).
4. **Render the SVG by default**: `bash <skill-dir>/scripts/render_mmd.sh <file.mmd> [more.mmd ...]` writes `<file>.svg` next to the source via `mmdc` and exits non-zero if any `@{ icon }` rendered as a `?` fallback. The default deliverable is **`.mmd` + `.svg` side by side**. If node/npx is unavailable the script prints SKIP — deliver the `.mmd` only and say so in the report. Render options (themes, PNG/PDF, parse-only check): [references/validation-rendering.md](references/validation-rendering.md).

### 7. Report back
- The file paths — both the `.mmd` source and the rendered `.svg` (or that SVG was skipped: no node/npx).
- A 3–6 bullet summary of the diagram's structure (subgraphs + main flow).
- Assumptions: what you included/excluded, which edges are optional (dotted), where to look for detail.
- How to render: open the `.mmd` in VS Code with the Mermaid Preview extension, paste it into a ` ```mermaid ` fenced block in a `.md` file, or run `mmdc -i file.mmd -o file.svg`.
- Offer 2–3 presentation options for the final view (theme, palette, hand-drawn look, export format) — see [references/styling-themes.md](references/styling-themes.md).

## Validation checklist (must all pass before delivering)
- [ ] Files are under `<target-dir>/diagrams/` (unless the user gave an explicit output path); the folder exists.
- [ ] First meaningful line is a valid diagram keyword.
- [ ] Every label is quoted; quotes balanced on every line; no raw `"` inside a label.
- [ ] Brackets `([{` balanced on every line.
- [ ] Every `subgraph` has a matching `end`.
- [ ] Only valid edge arrows used — flowchart: `-->`, `---`, `-- text -->`, `-.->`, `-. text .->`, `==>`, `== text ==>`, `<-->`, `x--x`, `o--o`; sequenceDiagram has its own (`->>`, `-->>`, `-x`, `--x`).
- [ ] No bare `%%` line — an empty comment is a Mermaid v11 parse error; always put text after `%%`.
- [ ] No node ID reused with a different shape; no reserved word used as an ID.
- [ ] ≤ ~30 nodes (aim ~10–15 per view); subgraphs used for layers/boundaries.
- [ ] In a multi-view set, every file's `%%` header cross-references the sibling views.
- [ ] `python3 <skill-dir>/scripts/check_mmd.py <file>` → PASS.
- [ ] `bash <skill-dir>/scripts/render_mmd.sh <file>` → OK, `<file>.svg` sits next to the source and its `>?</tspan>` icon check is clean (if node/npx missing: reported as skipped).

## Common pitfalls
- Unquoted labels containing `( ) [ ] { } : ; / ? & -- >` → parse error. Always quote.
- Missing `end` for a subgraph → "Parse error".
- A bare `%%` comment line (nothing after `%%`) → "Parse error" in Mermaid v11. Write `%% text`.
- Emoji in labels render inconsistently — use `@{ icon: "fa:..." }` instead.
- `@{ icon: ... }` requires Mermaid ≥ v11; `architecture-beta` requires ≥ v11.3. Update the VS Code preview extension if icons show as plain text.
- Very long labels break layout — wrap with `<br/>` or shorten.
- `TD` vs `LR`: TD for layered architecture, LR for left-to-right pipelines / CI flows.
- Arrowheads are SVG markers (`-->` = filled triangle). If a preview shows a box at a connection point, that renderer failed to draw the marker — the file is fine; verify via mermaid.live or `mmdc` export and update the preview extension. Change marker per edge with `---` (none) / `==>` (thick) / `o--o` / `x--x` / `<-->`; recolor all edges with `linkStyle default stroke:#...`. Details: [references/flowchart-syntax.md](references/flowchart-syntax.md).
- A `?` inside a node's icon box means an `@{ icon }` fallback: the icon pack (CDN, fetched at render time) failed to load. Not a syntax error. Fix by verifying the pack loads in the target renderer, or remove the `@{ icon: ... }` — then check the rendered SVG has no `>?</tspan>`.
- Never put secrets, tokens, or absolute local paths in the diagram.

## Resources
```
diagram-mmd/
├── SKILL.md                          # this file (only mandatory file per the spec)
├── scripts/
│   ├── check_mmd.py                  # stdlib-only .mmd linter — run before delivering
│   └── render_mmd.sh                 # renders <file>.svg next to each .mmd via mmdc + icon-fallback check — run by default
└── references/
    ├── diagram-types.md              # which diagram type to pick + minimal example each
    ├── flowchart-syntax.md           # shapes, edges, subgraphs, styling, icons, config
    ├── styling-themes.md             # 3 presentation options (theme / palette / hand-drawn) + export formats
    └── validation-rendering.md       # render/lint commands, VS Code setup, common errors
```
