"""Verify the asterisk sweep: no escapes left, and every line carrying a
starred question ref still renders with intact emphasis.

Usage:  python verify_starred_refs.py <knowledge-files-dir>
Requires: pip install commonmark
"""

import io
import re
import sys
from pathlib import Path

import commonmark

if len(sys.argv) < 2:
    sys.exit("usage: python verify_starred_refs.py <knowledge-files-dir>")
ROOT = Path(sys.argv[1])

REF = re.compile(r"Q\*[0-9]")
ITALIC_LABEL = re.compile(r"^\*Example", re.MULTILINE)

escapes = []
stray_italic_labels = []
broken = []
ref_lines = 0

for path in sorted(ROOT.rglob("*.md")):
    text = io.open(path, encoding="utf-8").read()

    if "Q\\*" in text:
        escapes.append(str(path.relative_to(ROOT)))
    for m in ITALIC_LABEL.finditer(text):
        stray_italic_labels.append(f"{path.relative_to(ROOT)}")
        break

    for i, line in enumerate(text.splitlines(), 1):
        if not REF.search(line):
            continue
        ref_lines += 1
        html = commonmark.commonmark(line)
        # The literal asterisk must survive; emphasis must not have eaten the ref.
        for m in REF.finditer(line):
            if m.group(0) not in html:
                broken.append(f"{path.relative_to(ROOT)}:{i}  {line[:110]}")
                break

print("lines carrying a starred ref:", ref_lines)
print("files still containing Q\\*:", escapes or "none")
print("files still using *Example italic labels:", stray_italic_labels or "none")
print("lines where the ref does not survive rendering:", len(broken))
for b in broken:
    print("  ", b)
