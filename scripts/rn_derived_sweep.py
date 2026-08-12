"""RN-derived marking-claim sweep — shortlist generator, NOT a gate (F149).

PACK PROVENANCE: specified by F149 (Leander Oates, 1PH0, 12 Aug 2026). The
1PH0 build carries its own scripts/rn_derived_sweep.py written that run; this
pack copy is a fresh implementation of the finding's published spec (the
project original was not available to import when the pack was hardened) —
reconcile the two when the project copy is upstreamed.

WHAT IT HUNTS (F148's class): sentences that assert marking behaviour —
how marks split, how often something is credited, what examiners "usually"
do — quantified over an unnamed set, sitting in a block with no paper-derived
support. On 1PH0 one such sentence generalised a revision-note claim the
corpus's own mark schemes contradict two-to-one, and every form/style gate
passed it.

WHY NOT THE OBVIOUS SWEEP: matching drafts against rn.md does NOT work.
Measured on the known-false 1PH0 claim: 0.000 5-gram overlap with the rn.md
passage it derives from — the writer paraphrases, so RN-derived content is
lexically invisible, and an overlap sweep returns a clean bill of health
across every file, which is worse than no sweep. The workable inverse: flag
the CLAIM SHAPE (marking vocabulary + unbounded quantifier) wherever its
containing block carries no paper reference.

BLOCK SCOPING (the ledger's method note, 12 Aug 2026): blocks are cut at
headings and callout boundaries, never a fixed line window — a line window
picks up references belonging to neighbouring prose and produces false
clears (both wrong numbers in the 1PH0 ledger were window-scoping artefacts).

OUTPUT: a shortlist for HUMAN adjudication. Exit 0 always (exit 2 only when
no files matched — a sweep of zero files must not read as clean, F69). It is
non-blocking by design: a large share of hits are legitimate verbatim
examiner-report quotation, so blocking would be wrong (F149). Run at
/hero-4-publish gate 2 alongside preflight_sweep.py's unbounded-quantifier
report (F120), and expect every hit to need judgement.

Usage:
  python rn_derived_sweep.py <file-or-dir> [more...]

Directories are swept recursively for *.md (excluding *.cobalt.md).
"""

import re
import sys
from pathlib import Path

# Quantifiers over an unnamed set — the F148 claim's signature ("almost
# always"), plus the F120 cousins.
QUANTIFIER_RE = re.compile(
    r"\b(?:almost always|almost every|usually|generally|typically|tends? to"
    r"|nearly always|in most cases|most(?:ly)?(?= \w)|always|never|every time"
    r"|invariably|routinely|often)\b", re.IGNORECASE)

# Marking-behaviour vocabulary — the sentence must be ABOUT marks/examiners,
# not merely about physics.
MARKING_RE = re.compile(
    r"\bmarks?\b|\bmark scheme|\bcredit(?:ed|s)?\b|\baccept(?:ed|s)?\b"
    r"|\breject(?:ed|s)?\b|\bexaminers?\b|\bawarded?\b|\becf\b"
    r"|\bmarking point|\bfull marks|\bone mark|\btwo marks|\bthree marks"
    r"|\bscores?\b|\bsplits? into\b", re.IGNORECASE)

# Paper-derived support: a question-part ref, a sitting, or a paper code
# inside the SAME block.
PAPER_REF_RE = re.compile(
    r"\bQ\d+|\b(?:19|20)\d\d\b.{0,40}?(?:January|February|March|April|May"
    r"|June|July|August|September|October|November|December)"
    r"|(?:January|February|March|April|May|June|July|August|September"
    r"|October|November|December)\b.{0,40}?\b(?:19|20)\d\d"
    r"|\bPaper \d", re.IGNORECASE | re.DOTALL)

# A block boundary is a heading or a callout opener; a blockquote run is part
# of the block it follows (marking banks are quoted under their claim).
BOUNDARY_RE = re.compile(r"^#{1,6}\s|^>\s*\[!")


def blocks(text):
    """Yield (start_line_1based, [lines]) cut at headings and callout openers."""
    cur_start, cur = 1, []
    for i, line in enumerate(text.splitlines(), 1):
        if BOUNDARY_RE.match(line) and cur:
            yield cur_start, cur
            cur_start, cur = i, []
        cur.append(line)
    if cur:
        yield cur_start, cur


def sweep_file(path):
    text = path.read_text(encoding="utf-8")
    hits = []
    for start, lines in blocks(text):
        block_text = "\n".join(lines)
        supported = bool(PAPER_REF_RE.search(block_text))
        for off, line in enumerate(lines):
            for m in QUANTIFIER_RE.finditer(line):
                # the quantifier and marking vocabulary must share a sentence,
                # not merely a block — a block-level AND over both patterns
                # flags every quantified physics fact near an unrelated mark
                sentence_start = max(line.rfind(". ", 0, m.start()),
                                     line.rfind("! ", 0, m.start()),
                                     line.rfind("? ", 0, m.start()))
                sentence_end = len(line)
                for p in (". ", "! ", "? "):
                    e = line.find(p, m.end())
                    if e != -1:
                        sentence_end = min(sentence_end, e + 1)
                sentence = line[sentence_start + 1:sentence_end]
                if MARKING_RE.search(sentence):
                    hits.append((start + off, supported, sentence.strip()))
                    break  # one hit per line
    return hits


def main():
    # cp1252 consoles crash on source glyphs (pi, mu, U+2212...) inside the
    # quoted sentences this script PRINTS -- reconfigure rather than requiring
    # PYTHONIOENCODING (same guard as spec_coverage_gate/fixer_diff_sweep;
    # caught on the first real run, an IAL master carrying a pi)
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    files = []
    for a in sys.argv[1:]:
        p = Path(a)
        if p.is_dir():
            files += sorted(f for f in p.rglob("*.md")
                            if not f.name.endswith(".cobalt.md"))
        else:
            files.append(p)

    if not files:
        print("SWEEP COULD NOT RUN: no files matched the given paths -- "
              "nothing was swept (a zero-file sweep must not read as clean, F69).")
        sys.exit(2)

    total = unsupported = 0
    for f in files:
        hits = sweep_file(f)
        if not hits:
            continue
        print(f"\n== {f.name}")
        for ln, supported, sentence in hits:
            total += 1
            unsupported += not supported
            tag = "block has paper ref" if supported else "NO PAPER SUPPORT IN BLOCK"
            print(f"  L{ln} [{tag}] {sentence[:160]}")

    print(f"\n{len(files)} files swept. {total} marking-claim candidate(s), "
          f"{unsupported} with no paper reference in their block.")
    print("Shortlist for HUMAN adjudication (F149) -- verbatim ER quotation is a "
          "legitimate hit; test each claim against ms-extracts.md, never against rn.md.")
    sys.exit(0)


if __name__ == "__main__":
    main()
