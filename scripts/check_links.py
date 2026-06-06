#!/usr/bin/env python3
"""Verify every `skills/...` / `.agents/...` / `.agent/...` file reference in the
adapter layer resolves to a real file. Catches broken Load-paths before runtime."""
import re, pathlib, sys

ROOT = pathlib.Path("/home/user/workspace/ars-antigravity")
# files that contain references we care about
SOURCES = [
    ROOT / "AGENTS.md", ROOT / "GEMINI.md", ROOT / "README.md",
    *(ROOT / ".agents").rglob("*.md"),
    *(ROOT / ".agent").rglob("*.md"),
    *(ROOT / "skills").glob("*/SKILL.md"),
]
# match backtick-quoted relative paths ending in a known extension
PATH_RE = re.compile(r"`([A-Za-z0-9_./-]+\.(?:md|json))`")
KNOWN_PREFIXES = ("skills/", ".agents/", ".agent/")

missing, checked = [], 0
for src in SOURCES:
    if not src.is_file():
        continue
    base = src.parent
    for m in PATH_RE.finditer(src.read_text(encoding="utf-8")):
        ref = m.group(1)
        if not ref.startswith(KNOWN_PREFIXES):
            continue  # skip prose like AGENTS.md, external, or upstream-internal relative refs
        checked += 1
        target = (ROOT / ref)
        # also allow refs relative to the source file (e.g. ../academic-paper/...)
        if not target.exists() and not (base / ref).exists():
            missing.append(f"{src.relative_to(ROOT)} -> {ref}")

print(f"Checked {checked} repo-rooted references across {len(SOURCES)} files.")
if missing:
    print(f"\n❌ {len(missing)} BROKEN references:")
    for x in missing[:40]:
        print("   " + x)
    sys.exit(1)
print("✅ All repo-rooted references resolve to real files.")
