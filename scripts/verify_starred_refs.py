"""Verify starred question refs: correct form, no escapes, and render survival.

F85: this gate previously did the opposite of its job -- its detection regex WAS
the defective form (Q*17), so it certified the bug as clean and went blind the
moment the bug was fixed. The board attaches the star to a PART, never to a main
question number (RULING W-34: 40/40 levelled rows across 20 mark schemes carry a
part letter). Detecting the correct form and the incorrect form are therefore
two different patterns:

  DEFECT  Q*17        -- star on a main number: a reference the board never
                         prints and a student cannot resolve. Any hit FAILS.
  CORRECT Q17(c)*     -- star on the part (optionally Q17(c)(ii)*). These are
                         render-checked: the literal asterisk must survive
                         markdown emphasis (e.g. a ref inside a bold citation
                         "**... Q9(c)***" loses its star to the closing bold).

Usage:  python verify_starred_refs.py <knowledge-files-dir> [more dirs...] [--min-ref-lines N]
All directory arguments are swept, recursively (F69: this script previously took
sys.argv[1] only and SILENTLY dropped every further argument -- on 1PH0 that hid
86 starred-ref lines behind a "clean" report with a non-zero file count).

--min-ref-lines N: fail (exit 2, GATE COULD NOT RUN) if fewer than N lines carry
a correct-form ref. F85: a gate whose finding count can legitimately reach zero
on correct content must be told the expected floor, or it silently becomes a
no-op -- on a wave known to cite levelled questions, pass the expected count.
Requires: pip install commonmark
"""

import io
import re
import sys
from pathlib import Path

import commonmark

argv = sys.argv[1:]
min_ref_lines = 0
if "--min-ref-lines" in argv:
    i = argv.index("--min-ref-lines")
    min_ref_lines = int(argv[i + 1])
    del argv[i:i + 2]

if not argv:
    sys.exit("usage: python verify_starred_refs.py <knowledge-files-dir> [more dirs...] [--min-ref-lines N]")
ROOTS = [Path(a) for a in argv]
bad = [str(r) for r in ROOTS if not r.is_dir()]
if bad:
    print(f"GATE COULD NOT RUN: not a directory: {', '.join(bad)}")
    sys.exit(2)

DEFECT_REF = re.compile(r"Q\*[0-9]+")                            # star on a main number (W-34: never printed by the board)
CORRECT_REF = re.compile(r"Q[0-9]+\s*\([a-z]\)(?:\([ivxl]+\))?\*")  # star on the part -- the only resolvable form
ITALIC_LABEL = re.compile(r"^\*Example", re.MULTILINE)

escapes = []
defective = []
stray_italic_labels = []
broken = []
ref_lines = 0
scanned = 0

for ROOT in ROOTS:
  for path in sorted(ROOT.rglob("*.md")):
    scanned += 1
    text = io.open(path, encoding="utf-8").read()

    if "Q\\*" in text or ")\\*" in text:
        escapes.append(str(path.relative_to(ROOT)))
    for m in ITALIC_LABEL.finditer(text):
        stray_italic_labels.append(f"{path.relative_to(ROOT)}")
        break

    for i, line in enumerate(text.splitlines(), 1):
        for m in DEFECT_REF.finditer(line):
            # Skip when this is really a correct-form ref whose main number the
            # defect regex grazed (no such overlap exists, but stay explicit)
            defective.append(f"{path.relative_to(ROOT)}:{i}  {m.group(0)}  {line[:90]}")
        if not CORRECT_REF.search(line):
            continue
        ref_lines += 1
        html = commonmark.commonmark(line)
        # The literal asterisk must survive; emphasis must not have eaten the
        # ref (a part-form ref inside a bold citation is the known breakage --
        # "**2023 June Paper 1H, Q9(c)***" renders the star OUTSIDE the bold)
        for m in CORRECT_REF.finditer(line):
            if m.group(0) not in html:
                broken.append(f"{path.relative_to(ROOT)}:{i}  {line[:110]}")
                break

if scanned == 0:
    # F69: this script once reported clean having swept zero files -- a
    # verification that read nothing must fail loudly, never print "none"
    print(f"GATE COULD NOT RUN: no .md files found under {', '.join(map(str, ROOTS))} -- nothing was verified.")
    sys.exit(2)

print("files scanned:", scanned)
print("lines carrying a correct-form starred ref (Qn(x)*):", ref_lines)
print("DEFECTIVE main-number starred refs (Q*n -- W-34, the board never prints this):", len(defective))
for d in defective:
    print("  ", d)
print("files containing escaped starred refs (Q\\* or )\\*):", escapes or "none")
print("files still using *Example italic labels:", stray_italic_labels or "none")
print("lines where a correct-form ref does not survive rendering:", len(broken))
for b in broken:
    print("  ", b)

if ref_lines < min_ref_lines:
    # F85 fix 2: zero (or too few) matches on a wave that should have them is
    # "did not run", not "passed"
    print(f"GATE COULD NOT RUN as specified: {ref_lines} correct-form ref line(s) found, "
          f"--min-ref-lines {min_ref_lines} expected -- the sweep may be looking at the wrong tree or the wrong form.")
    sys.exit(2)
if ref_lines == 0 and not defective:
    print("note: zero starred refs found in either form. If this wave cites levelled "
          "questions, that is itself suspicious -- consider --min-ref-lines with the expected count.")

# Defects found must set a non-zero exit -- a caller reading only the exit code
# previously saw success regardless of what was printed
if escapes or stray_italic_labels or broken or defective:
    sys.exit(1)
