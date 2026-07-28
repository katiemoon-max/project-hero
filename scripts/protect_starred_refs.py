"""Protect starred question refs from markdown emphasis pairing.

Standing rule: write starred refs as Q*17, never Q\\*17 (the backslash renders
literally in Cobalt). The cost is that a bare '*' is a live emphasis delimiter,
so a line carrying two refs -- or one ref plus any other italic/bold run -- can
have its asterisks pair up and swallow the text between them.

This is a build-time guard, not a style rule: the writer always types Q*17
plain. Here we render each line and, only where a ref does not survive intact,
wrap that line's refs in ** ** (a single '*' inside a strong span is inert,
because the emphasis algorithm's multiple-of-three rule refuses the pairing).

Also finishes the label sweep: line-initial *Example ...* italic labels are
promoted to bold (the bold Example label is what shields most refs).

Usage:  python protect_starred_refs.py <knowledge-files-dir> [--apply]
Dry run by default; pass --apply to write changes.
Requires: pip install commonmark
"""

import io
import re
import sys
from pathlib import Path

import commonmark

args = [a for a in sys.argv[1:] if a != "--apply"]
if not args:
    sys.exit("usage: python protect_starred_refs.py <knowledge-files-dir> [--apply]")
ROOT = Path(args[0])
apply = "--apply" in sys.argv

REF = re.compile(r"(?<!\*)Q\*[0-9]+")
LABEL_RE = re.compile(r"^\*(Examples?[^\n]*?[:,.])\*(?=\s|$)", re.MULTILINE)


def ref_survives(line: str) -> bool:
    html = commonmark.commonmark(line)
    return all(m.group(0) in html for m in REF.finditer(line))


totals = {"labels": 0, "protected_lines": 0, "protected_refs": 0, "files": 0}

for path in sorted(ROOT.rglob("*.md")):
    if path.name.endswith(".cobalt.md"):
        continue
    text = io.open(path, encoding="utf-8").read()
    original = text

    text, n_lab = LABEL_RE.subn(r"**\1**", text)

    out = []
    n_lines = n_refs = 0
    for line in text.split("\n"):
        if REF.search(line) and not ref_survives(line):
            fixed = REF.sub(lambda m: f"**{m.group(0)}**", line)
            if ref_survives(fixed):
                n_lines += 1
                n_refs += len(REF.findall(line))
                line = fixed
            else:
                print(f"  !! UNFIXED {path.relative_to(ROOT)}: {line[:90]}")
        out.append(line)
    text = "\n".join(out)

    if text != original:
        totals["files"] += 1
        totals["labels"] += n_lab
        totals["protected_lines"] += n_lines
        totals["protected_refs"] += n_refs
        print(f"{path.relative_to(ROOT)}: labels {n_lab}, protected lines {n_lines}")
        if apply:
            io.open(path, "w", encoding="utf-8", newline="\n").write(text)

print()
print(("APPLIED" if apply else "DRY RUN"), totals)
