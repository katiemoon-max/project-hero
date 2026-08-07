"""Verify the asterisk sweep: no escapes left, and every line carrying a
starred question ref still renders with intact emphasis.

Usage:  python verify_starred_refs.py <knowledge-files-dir> [more dirs...]
All directory arguments are swept, recursively (F69: this script previously took
sys.argv[1] only and SILENTLY dropped every further argument -- on 1PH0 that hid
86 starred-ref lines behind a "clean" report with a non-zero file count).
Requires: pip install commonmark
"""

import io
import re
import sys
from pathlib import Path

import commonmark

if len(sys.argv) < 2:
    sys.exit("usage: python verify_starred_refs.py <knowledge-files-dir> [more dirs...]")
ROOTS = [Path(a) for a in sys.argv[1:]]
bad = [str(r) for r in ROOTS if not r.is_dir()]
if bad:
    print(f"GATE COULD NOT RUN: not a directory: {', '.join(bad)}")
    sys.exit(2)

REF = re.compile(r"Q\*[0-9]")
ITALIC_LABEL = re.compile(r"^\*Example", re.MULTILINE)

escapes = []
stray_italic_labels = []
broken = []
ref_lines = 0
scanned = 0

for ROOT in ROOTS:
  for path in sorted(ROOT.rglob("*.md")):
    scanned += 1
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

if scanned == 0:
    # F69: this script once reported clean having swept zero files -- a
    # verification that read nothing must fail loudly, never print "none"
    print(f"GATE COULD NOT RUN: no .md files found under {', '.join(map(str, ROOTS))} -- nothing was verified.")
    sys.exit(2)

print("files scanned:", scanned)
print("lines carrying a starred ref:", ref_lines)
print("files still containing Q\\*:", escapes or "none")
print("files still using *Example italic labels:", stray_italic_labels or "none")
print("lines where the ref does not survive rendering:", len(broken))
for b in broken:
    print("  ", b)
# Defects found must set a non-zero exit -- a caller reading only the exit code
# previously saw success regardless of what was printed
if escapes or stray_italic_labels or broken:
    sys.exit(1)
