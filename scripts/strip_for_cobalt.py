"""Strip Obsidian-flavoured formatting from a knowledge file for Cobalt upload.

The Cobalt document viewer renders plain markdown: it does not understand
Obsidian callouts (> [!tip] / > [!warning]) or blockquotes — the raw ">"
markers show as literal text. The vault master files KEEP callouts (they are
the proofing markers for Claude-authored layers); this script produces the
upload variant:

- ``> [!tip] Title``  -> heading one level below the enclosing section, title unchanged
- ``> [!warning] Title`` -> same, with " (Common Error)" appended unless the
  title already mentions errors
- Callout body lines lose their "> " prefix (blank "> " lines become blank lines)
- ``> **Specification:** ...`` (and any other plain blockquote) loses its "> " prefix

Usage:  python strip_for_cobalt.py "<input.md>" ["<output.md>"]
If no output path is given, writes alongside the input as *.cobalt.md.
Idempotent: running on an already-stripped file changes nothing.
"""

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
            if kind == "warning" and "error" not in title.lower():
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
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2]) if len(sys.argv) > 2 else src.with_suffix(".cobalt.md")
    dst.write_text(strip_for_cobalt(src.read_text(encoding="utf-8")), encoding="utf-8")
    print(f"written: {dst}")


if __name__ == "__main__":
    main()
