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
                         markdown rendering.

F158 (18 Aug 2026): the old CORRECT pattern ended in a bare `\\*`, so on a
bold-terminated line it matched the first asterisk of the CLOSING `**`:

  **Worked Example -- 2020 November Paper 1F, Q9(b)(ii)**

carries no star, and every plain bolded worked-example label on a course
tripped it. Measured on 1PH0 (96 files): 224 of 488 "starred" lines carried no
star, and ALL 318 reported render failures were false. The obvious fix,
`(?!\\*)`, is WRONG and worse than the bug: it rejects `Q9(c)***` -- a GENUINE
star followed by a closing `**` -- turning a loud false positive into a silent
false negative. What works is capturing the asterisk RUN after the ref and
taking its parity: odd = a literal star is present, even = bare emphasis
delimiters only. The render check then compares against the TAG-STRIPPED HTML,
so the ruled star-outside-the-bold form (F122(2): `**...Q9(c)***` renders as
bold text + unbolded star -- the accepted convention) passes instead of being
reported as a break.

KNOWN LIMIT, documented rather than engineered around: an *italic*-wrapped ref
misreads under parity (the italic delimiters shift the run by one). The pack
emits no italic-wrapped refs -- the ITALIC_LABEL check below exists to keep it
that way -- so parity holds. If a course ever adopts italic citations, this
gate needs emphasis STATE tracked through the line, not run length.

Usage:  python verify_starred_refs.py <knowledge-files-dir> [more dirs...] [--min-ref-lines N]
All directory arguments are swept, recursively (F69: this script previously took
sys.argv[1] only and SILENTLY dropped every further argument -- on 1PH0 that hid
86 starred-ref lines behind a "clean" report with a non-zero file count).

--min-ref-lines N: fail (exit 2, GATE COULD NOT RUN) if fewer than N lines carry
a genuinely starred ref. F85: a gate whose finding count can legitimately reach
zero on correct content must be told the expected floor, or it silently becomes
a no-op -- on a wave known to cite levelled questions, pass the expected count.
Note the F158 fix LOWERS this count against pre-fix runs (1PH0: 488 -> 264) --
recalibrate any recorded floor after adopting it.
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
# F158: capture the ref and its trailing asterisk RUN separately; parity of the
# run decides whether a literal star is present (odd) or the asterisks are bare
# emphasis delimiters (even -- e.g. the closing ** of a bold label line)
REF_RUN = re.compile(r"(Q[0-9]+\s*\([a-z]\)(?:\([ivxl]+\))?)(\*+)")
ITALIC_LABEL = re.compile(r"^\*Example", re.MULTILINE)
HTML_TAG = re.compile(r"<[^>]+>")

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
            defective.append(f"{path.relative_to(ROOT)}:{i}  {m.group(0)}  {line[:90]}")
        starred = [(m.group(1), m.group(2)) for m in REF_RUN.finditer(line)
                   if len(m.group(2)) % 2 == 1]
        if not starred:
            continue
        ref_lines += 1
        # The literal asterisk must survive rendering. Compare against the
        # TAG-STRIPPED text of the rendered line (F158): the star may legally
        # sit outside a closing </strong> (F122(2)) -- what matters is that
        # ref + star both reach the reader, not where the tags fall
        rendered = HTML_TAG.sub("", commonmark.commonmark(line))
        for base, run in starred:
            if base + "*" not in rendered:
                broken.append(f"{path.relative_to(ROOT)}:{i}  {line[:110]}")
                break

if scanned == 0:
    # F69: this script once reported clean having swept zero files -- a
    # verification that read nothing must fail loudly, never print "none"
    print(f"GATE COULD NOT RUN: no .md files found under {', '.join(map(str, ROOTS))} -- nothing was verified.")
    sys.exit(2)

print("files scanned:", scanned)
print("lines carrying a genuinely starred ref (Qn(x)*, odd asterisk run):", ref_lines)
print("DEFECTIVE main-number starred refs (Q*n -- W-34, the board never prints this):", len(defective))
for d in defective:
    print("  ", d)
print("files containing escaped starred refs (Q\\* or )\\*):", escapes or "none")
print("files still using *Example italic labels:", stray_italic_labels or "none")
print("lines where a starred ref does not survive rendering (star absent from tag-stripped output):", len(broken))
for b in broken:
    print("  ", b)

if ref_lines < min_ref_lines:
    # F85 fix 2: zero (or too few) matches on a wave that should have them is
    # "did not run", not "passed"
    print(f"GATE COULD NOT RUN as specified: {ref_lines} starred ref line(s) found, "
          f"--min-ref-lines {min_ref_lines} expected -- the sweep may be looking at the wrong tree or the wrong form.")
    sys.exit(2)
if ref_lines == 0 and not defective:
    print("note: zero starred refs found in either form. If this wave cites levelled "
          "questions, that is itself suspicious -- consider --min-ref-lines with the expected count.")

# Defects found must set a non-zero exit -- a caller reading only the exit code
# previously saw success regardless of what was printed
if escapes or stray_italic_labels or broken or defective:
    sys.exit(1)
