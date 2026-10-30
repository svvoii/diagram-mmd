#!/usr/bin/env bash
# render_mmd.sh — render .mmd files to sibling .svg files with mermaid-cli (mmdc),
# then verify that no @{ icon } fell back to a literal "?" glyph.
#
# Usage:
#   bash scripts/render_mmd.sh path/to/diagram.mmd [more.mmd ...]
#
# Behaviour:
#   - node/npx missing       -> prints SKIP, exits 0 (deliver the .mmd only)
#   - render ok, 0 "?" icons -> writes <file>.svg, prints OK, exits 0
#   - any "?" icon fallback  -> still writes the svg, prints FAIL, exits 1
#     (remove the @{ icon: ... } from the .mmd, or make the icon pack loadable,
#      then re-run)
set -uo pipefail

if ! command -v npx >/dev/null 2>&1; then
  echo "SKIP: node/npx not available — no SVG generated (lint-only delivery)"
  exit 0
fi

fail=0
for f in "$@"; do
  out="${f%.mmd}.svg"
  if ! npx --yes @mermaid-js/mermaid-cli -i "$f" -o "$out" -b white; then
    echo "FAIL: $f did not render"
    fail=1
    continue
  fi
  q=$(grep -c '>?</tspan>' "$out" || true)
  if [ "$q" != "0" ]; then
    echo "FAIL: $out has $q unresolved icon(s) ('?' fallback) — remove @{ icon: ... } or fix the icon pack, then re-run"
    fail=1
  else
    echo "OK: $f -> $out"
  fi
done
exit $fail
