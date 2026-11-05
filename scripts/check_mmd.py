#!/usr/bin/env python3
"""
check_mmd.py — sanity linter for Mermaid (.mmd) files. Python stdlib only.

Usage:
    python3 scripts/check_mmd.py path/to/diagram.mmd [more.mmd ...]

Checks:
  E1  file readable as UTF-8
  E2  first meaningful line starts with a known diagram keyword
  E3  double quotes balanced on every line (labels must not span lines)
  E4  (), [], {} balanced on every line (outside quoted strings)
  E5  every `subgraph` has a matching `end`, no stray `end`
  E6  no invalid arrow tokens (flowchart/graph only — other diagram types
      have their own arrow syntax and are skipped here)
  E7  no bare `%%` comment line (empty comment breaks the Mermaid v11 parser)
  W1  node ID reused with a different shape
  W2  emoji / pictographs present (render inconsistently)
  W3  tab characters (use spaces)
  W4  reserved word used as a node ID
  W5  `@{...}` metadata used (icons/shapes) — icons need Mermaid >= v11 and a
      loadable icon pack (fetched from a CDN at render time); on failure the
      icon renders as a literal '?' in the output SVG

Exit code 0 = PASS (warnings allowed), 1 = FAIL (at least one E* error).
"""

import re
import sys

KEYWORDS = {
    "flowchart", "graph", "sequencediagram", "classdiagram", "statediagram",
    "statediagram-v2", "erdiagram", "journey", "gantt", "pie", "quadrantchart",
    "requirementdiagram", "gitgraph", "mindmap", "timeline", "c4context",
    "c4container", "c4component", "c4dynamic", "c4deployment", "architecture-beta",
    "block-beta", "packet-beta", "sankey-beta", "xychart", "radar-beta",
    "kanban-beta",
}

RESERVED = {
    "end", "graph", "flowchart", "subgraph", "direction", "click", "call",
    "style", "class", "classdef", "linkstyle", "callback",
}

# Longest-first alternation of valid edge arrows.
ARROW_RE = re.compile(
    r"<-->|-\.->|-->|<--|\.->|x--x|o--o|---|===|==>|--|==|-\.|x--|o--"
)
NODE_DEF_RE = re.compile(r"\b([A-Za-z][A-Za-z0-9_]*)\s*([\[\(\{])")


def clean_line(line):
    """Remove %% comments and quoted strings (quoted strings -> empty)."""
    out = []
    in_quote = False
    i = 0
    while i < len(line):
        c = line[i]
        if c == '"':
            in_quote = not in_quote
            i += 1
            continue
        if not in_quote and line.startswith("%%", i):
            break
        if not in_quote:
            out.append(c)
        i += 1
    return "".join(out), in_quote


def check_file(path):
    errors = []
    warnings = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
    except (OSError, UnicodeDecodeError) as e:
        return [f"E1: cannot read {path} as UTF-8: {e}"], []

    # E2: first meaningful line = diagram keyword (skip blanks, comments,
    # directives, and a leading YAML frontmatter block).
    in_frontmatter = False
    keyword_found = False
    diag = None
    for n, raw in enumerate(lines, 1):
        s = raw.strip()
        if s == "---":
            in_frontmatter = not in_frontmatter
            continue
        if in_frontmatter or not s or s.startswith("%%"):
            continue
        token = s.split()[0].lower().rstrip(":")
        if token in KEYWORDS:
            keyword_found = True
            diag = token
        else:
            errors.append(f"line {n}: E2: first diagram line is {s[:40]!r} — "
                          f"expected a keyword like 'flowchart TD'")
        break
    if not keyword_found and lines:
        if not any(l.strip() and not l.strip().startswith("%%") for l in lines):
            errors.append("E2: file has no diagram content")

    depth = 0
    shapes = {}  # node id -> set of opening shape chars
    for n, raw in enumerate(lines, 1):
        if "\t" in raw:
            warnings.append(f"line {n}: W3: tab character (use spaces)")
        for ch in raw:
            o = ord(ch)
            if o >= 0x1F000 or 0x2600 <= o <= 0x27BF or o == 0xFE0F:
                warnings.append(f"line {n}: W2: emoji/pictograph U+{o:04X} — "
                                f"use @{{ icon: ... }} instead")
                break
        cleaned, in_quote = clean_line(raw)
        if in_quote:
            errors.append(f"line {n}: E3: unbalanced double quotes")
        if re.fullmatch(r"%%\s*", raw):
            errors.append(f"line {n}: E7: bare '%%' comment line — Mermaid v11 "
                          f"parse error; always put text after %%")
        if "@{" in cleaned:
            warnings.append(f"line {n}: W5: '@{{...}}' node metadata (icon/shape) — "
                            f"icons need Mermaid >= v11 + a loadable icon pack; if the "
                            f"pack fails to load the icon renders as '?' in the SVG "
                            f"(check: grep -c '>?</tspan>' out.svg must be 0)")

        # E4: bracket balance outside quotes
        stack = []
        pairs = {")": "(", "]": "[", "}": "{"}
        bad = None
        for ch in cleaned:
            if ch in "([{":
                stack.append(ch)
            elif ch in ")]}":
                if not stack or stack[-1] != pairs[ch]:
                    bad = ch
                    break
                stack.pop()
        if bad or stack:
            errors.append(f"line {n}: E4: unbalanced brackets "
                          f"(leftover {''.join(stack) or bad!r})")

        # E5: subgraph / end pairing
        if re.match(r"\s*subgraph\b", cleaned):
            depth += 1
        elif re.match(r"\s*end\b", cleaned):
            depth -= 1
            if depth < 0:
                errors.append(f"line {n}: E5: stray 'end' without subgraph")
                depth = 0

        # E6: invalid arrows (flowchart/graph only)
        if diag in ("flowchart", "graph"):
            no_arrows = ARROW_RE.sub(" ", cleaned)
            m = re.search(r"->|<-|=>|=<", no_arrows)
            if m:
                errors.append(f"line {n}: E6: invalid arrow token {m.group(0)!r} "
                              f"in {raw.strip()[:60]!r}")

        # W1/W4: node definitions
        for nid, shape in NODE_DEF_RE.findall(cleaned):
            if nid.lower() in RESERVED:
                warnings.append(f"line {n}: W4: reserved word {nid!r} used as node ID")
            shapes.setdefault(nid, set()).add(shape)
    if depth != 0:
        errors.append(f"E5: {depth} subgraph(s) without matching 'end'")

    for nid, ss in shapes.items():
        if len(ss) > 1:
            warnings.append(f"W1: node ID {nid!r} defined with multiple shapes "
                            f"{sorted(ss)} — make IDs unique")

    return errors, warnings


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    all_errors = []
    for path in argv[1:]:
        errors, warnings = check_file(path)
        for w in warnings:
            print(f"{path}: {w}")
        for e in errors:
            print(f"{path}: {e}")
        if errors:
            all_errors.extend(errors)
            print(f"{path}: FAIL ({len(errors)} error(s), {len(warnings)} warning(s))")
        else:
            print(f"{path}: PASS ({len(warnings)} warning(s))")
    return 1 if all_errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
