"""Strip Obsidian-flavoured formatting from a knowledge file for Cobalt upload.

The Cobalt document viewer renders plain markdown: it does not understand
Obsidian callouts (> [!tip] / > [!warning]) or blockquotes — the raw ">"
markers show as literal text. The vault master files KEEP callouts (they are
the proofing markers for Claude-authored layers); this script produces the
upload variant:

- ``> [!tip] Title``  -> heading one level below the enclosing section, title unchanged
- ``> [!warning] Title`` -> same, with " (Common Error)" appended unless the
  title already mentions errors
- **UNTITLED callouts get the house default label (F70)**: ``> [!tip]`` ->
  "Examiner Tips & Tricks", ``> [!warning]`` -> "Common Error". The untitled
  form is valid Obsidian and was the pack's own documented style for a whole
  course -- 227 of 227 callouts on 1PH0 reached Cobalt as EMPTY headings
  (``#### `` / ``####  (Common Error)``), erasing the tip/warning label from
  every chunk the heading was supposed to name. WRITER.md now asks for titles;
  this default is the backstop for the shape nothing enforces
- Callout body lines lose their "> " prefix (blank "> " lines become blank lines)
- ``> **Specification:** ...`` (and any other plain blockquote) loses its "> " prefix

Usage:  python strip_for_cobalt.py <file-or-dir> [more files/dirs...]
        python strip_for_cobalt.py <input.md> -o <output.md>   # single file only

Each input file writes alongside itself as *.cobalt.md; a directory strips
every non-.cobalt .md beneath it. Idempotent: running on an already-stripped
file changes nothing.

DESTINATION SAFETY (2026-08-10): the old positional [src, dst] argv meant a
multi-file call silently clobbered the SECOND file with the stripped content
of the first — it overwrote a verified master, recovered only because git held
it. Every destination is validated BEFORE anything is written, and a
destination that exists as a non-.cobalt file is REFUSED: this script only
ever writes *.cobalt.md.
"""

import argparse
import re
import sys
from pathlib import Path

CALLOUT_RE = re.compile(r"^>\s*\[!(?P<kind>\w+)\]\s*(?P<title>.*)$")
HEADING_RE = re.compile(r"^(?P<hashes>#{1,6})\s")


def strip_for_cobalt(text: str) -> str:
    out = []
    current_level = 1
    in_callout = False

    for line in text.splitlines():
        heading = HEADING_RE.match(line)
        if heading:
            current_level = len(heading.group("hashes"))
            in_callout = False
            out.append(line)
            continue

        callout = CALLOUT_RE.match(line)
        if callout:
            kind = callout.group("kind").lower()
            title = callout.group("title").strip()
            if not title:
                # F70: never emit an empty heading -- the heading is the
                # chunk's only label in Cobalt retrieval. Non-house kinds
                # (which CHECKER should have flagged) fall back to their kind
                title = {"tip": "Examiner Tips & Tricks",
                         "warning": "Common Error"}.get(kind, kind.title())
            elif kind == "warning" and "error" not in title.lower():
                title += " (Common Error)"
            level = min(current_level + 1, 6)
            out.append(f"{'#' * level} {title}")
            out.append("")
            in_callout = True
            continue

        if line.startswith(">"):
            stripped = line[1:]
            if stripped.startswith(" "):
                stripped = stripped[1:]
            out.append(stripped)
            continue

        # A non-quoted line ends any callout body
        if in_callout and line.strip():
            in_callout = False
        out.append(line)

    # Collapse any triple blank lines introduced by the conversion
    result = "\n".join(out)
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result.rstrip() + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Strip Obsidian callouts/blockquotes for Cobalt upload. "
        "Accepts files and directories; writes *.cobalt.md beside each master.")
    ap.add_argument("inputs", nargs="+", metavar="file-or-dir")
    ap.add_argument("-o", "--output",
                    help="explicit destination — allowed with exactly one input FILE")
    ns = ap.parse_args()

    srcs = []
    for a in ns.inputs:
        p = Path(a)
        if p.is_dir():
            srcs.extend(sorted(f for f in p.rglob("*.md")
                               if not f.name.endswith(".cobalt.md")))
        elif p.is_file():
            srcs.append(p)
        else:
            sys.exit(f"REFUSED: input not found: {p}")

    if ns.output and (len(ns.inputs) > 1 or len(srcs) != 1):
        sys.exit("REFUSED: --output takes exactly one input file — with several "
                 "inputs each master writes its own *.cobalt.md sibling")
    for src in srcs:
        if src.name.endswith(".cobalt.md"):
            sys.exit(f"REFUSED: {src} is already a stripped .cobalt.md — "
                     "pass the master, not the output")

    # Validate EVERY destination before writing ANY — a bad second argument
    # must not cost the first file's already-written output its master
    jobs = []
    for src in srcs:
        dst = Path(ns.output) if ns.output else src.with_suffix(".cobalt.md")
        if dst.exists() and not dst.name.endswith(".cobalt.md"):
            sys.exit(f"REFUSED: destination {dst} exists and is not a "
                     ".cobalt.md file — this script never overwrites a master")
        jobs.append((src, dst))

    for src, dst in jobs:
        dst.write_text(strip_for_cobalt(src.read_text(encoding="utf-8")), encoding="utf-8")
        print(f"written: {dst}")


if __name__ == "__main__":
    main()
