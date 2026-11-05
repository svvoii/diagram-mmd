# diagram-mmd

An [Agent Skills](https://agentskills.io/home) skill that turns a codebase, system, or
process into **Mermaid (`.mmd`) diagrams** — validated and rendered to SVG by default.
Use it when a user asks for a diagram, flowchart, architecture overview, or a visual
explanation of how a system or code path works.

## What it produces

For a target directory the agent writes diagrams to `<target-dir>/diagrams/`
(created if missing; an explicit user path always wins):

```
<target-dir>/diagrams/
├── architecture.mmd      # source, editable
├── architecture.svg      # rendered next to it by default
└── ...                   # one .mmd + .svg per view
```

Large systems are split into multiple views (overview + detail files) in the same
folder. Renders anywhere Mermaid does: VS Code Mermaid Preview, https://mermaid.live,
or `mmdc`.

## Layout

```
diagram-mmd/
├── SKILL.md                 # the skill: frontmatter + 7-step workflow (only mandatory file)
├── scripts/
│   ├── check_mmd.py         # stdlib-only .mmd linter — must PASS before delivery
│   └── render_mmd.sh        # .mmd -> sibling .svg via mmdc + "?" icon-fallback check — default step
└── references/              # loaded on demand: diagram-types, flowchart-syntax,
                             # styling-themes (theme/palette/hand-drawn/export), validation-rendering
```

## Quick commands

```bash
python3 scripts/check_mmd.py diagrams/architecture.mmd   # lint: exit 0 = PASS
bash scripts/render_mmd.sh diagrams/*.mmd                 # render SVGs + icon check
```

House style applied by default: `flowchart TD|LR`, quoted labels, subgraphs per layer,
`classDef` palette, `linkStyle default stroke:#607D8B,stroke-width:1.5px`, no icons unless
the renderer's icon pack is verified (icons otherwise render as `?`).

See `SKILL.md` for the full workflow, validation checklist, and pitfalls
(bare `%%` lines and unquoted labels are parse errors in Mermaid v11).
