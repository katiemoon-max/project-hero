"""Mechanical pre-strip/pre-upload sweep for Project Hero knowledge files.

Codifies the checks that were run ad hoc each wave, so nothing is re-derived
(or forgotten) per wave. Run on the MASTER .md files before strip_for_cobalt.py,
then again on the .cobalt.md variants before upload (cobalt mode adds the
callout/blockquote checks that only apply to the stripped variant).

FAIL checks (any hit blocks upload):
  - Mathematical Alphanumeric Symbols U+1D400-U+1D7FF (pasted from converted
    mark schemes; look like italics, break Cobalt fonts and search)
  - Private Use Area characters U+E000-U+F8FF (F97: Pearson symbol fonts map
    content glyphs -- half, delta, theta, degree, ohm -- to PUA codepoints that
    render as NOTHING; one reaching a knowledge file means a quoted equation is
    silently missing a symbol. Tabulated per codepoint, never in aggregate)
  - Escaped starred refs "Q\\*" — counted at byte level with text.count,
    NOT a regex (a regex once produced a multi-file false positive)
  - LaTeX \\Delta inside the file (house rule: Unicode increment U+2206)
  - Bare U+0394 GREEK CAPITAL DELTA (Round 12, 19 Aug 2026: the gate above
    NAMED the U+0394 half of Katie's ruling in its own message but never
    tested for it -- 5 instances across 2 wave-2 masters would have shipped
    clean; found by the 1PH0 Kinetic Energy checker. Leander's project added
    this gate locally on 17 Aug -- reconcile her copy on her next re-pull)
  - RN commentary syntax "$c{"
  - Images "![" and http(s) links
  - [cobalt mode only] Obsidian callouts "[!" and leading "> " blockquotes

REPORT checks (listed for orchestrator/fixer attention, not auto-failed):
  - Oxford comma candidates: ", and "/", or " closing a list — i.e. the
    segment back to the previous comma is short (<= 4 words) and does not
    open with a clause connective (which/who/where/so/but/because/though/
    giving/leaving/making). Review each hit; compound-sentence commas are
    legitimate and are NOT flagged
  - Flag-block parity: per file, count of "## Spec Point:" (SP) vs
    "**Key terminology:**" (KT) vs the skills line (SK, label per
    --skills-label). SP must equal KT in every file. SK = SP minus the SPs
    whose vault note carries the project's no-skills marker — validate the
    printed totals against the wave's OWN ruling list, never a handover's
    stated expectation (a handover's counts have been wrong before)
  - Unverified-claim vocabulary (F109/F111/F106): "lost in conversion",
    "did not survive conversion", "not recoverable", "cannot render",
    "is not installed", "physically unavailable", "this environment cannot".
    Each such claim must sit next to a list of the verification routes actually
    tried (second-engine markdown, PDF text layer, rendered page image) -- a
    claim naming a process or a tool where it should name a file/capability is
    an inference from a sample of one. Review each hit against its context
  - Unbounded quantifiers (F120): "every ... scheme" / "every Paper" without an
    enumerated list in the same block -- a true observation inflated over a set
    the note cannot have checked. Verify or re-scope each hit
  - Worked-example provenance (F150): every block opened by a "**Worked
    Example" label must carry a paper reference INSIDE that block (Qn / Paper n
    / sitting). Scoped from the label line to the next heading or next label,
    NEVER a fixed line window -- a window-scoped detector counted neighbouring
    prose's references and cleared an invented example it had not checked (the
    1PH0 ledger's "6 of 6 cite a paper" was really 2 of 6). 4 of 6 examples on
    the exposing wave had no reference at all; one was an rn.md import no
    student ever sat (F148). Reported, not auto-failed: the CHECKER blocks
    these (bare unattributed worked examples are BLOCKERS since F148/F150) --
    this sweep is the mechanical safety net at publish

Usage:
  python preflight_sweep.py <file-or-dir> [more...] [--cobalt] [--skills-label "Mathematical skills"]

Directories are swept for *.md (excluding *.cobalt.md unless --cobalt, in
which case ONLY *.cobalt.md are swept). Exit code 1 if any FAIL check hits.
"""

import re
import sys
from pathlib import Path

MATH_ALNUM_RE = re.compile("[\U0001D400-\U0001D7FF]")
PUA_RE = re.compile("[\uE000-\uF8FF]")
OXFORD_RE = re.compile(r",\s+(?:and|or)\s")
CLAIM_RE = re.compile(r"lost in conversion|did not survive conversion|not recoverable"
                      r"|cannot render|is not installed|physically unavailable"
                      r"|this environment cannot", re.IGNORECASE)
QUANTIFIER_RE = re.compile(r"\bevery (?:one of )?(?:the )?(?:mark )?scheme|\bevery Paper", re.IGNORECASE)
WE_LABEL_RE = re.compile(r"\*\*Worked Example")
PAPER_REF_RE = re.compile(
    r"\bQ\d+|\bPaper \d"
    r"|\b(?:19|20)\d\d\b.{0,40}?(?:January|February|March|April|May|June|July"
    r"|August|September|October|November|December)"
    r"|(?:January|February|March|April|May|June|July|August|September"
    r"|October|November|December)\b.{0,40}?\b(?:19|20)\d\d",
    re.IGNORECASE | re.DOTALL)


CLAUSE_OPENERS = ("which", "who", "where", "so", "but", "because", "though",
                  "giving", "leaving", "making", "and", "or", "not", "then")


def looks_like_list(line: str, match_start: int) -> bool:
    prev_comma = line.rfind(",", 0, match_start)
    sentence_start = line.rfind(". ", 0, match_start)
    if prev_comma <= sentence_start:
        return False
    segment = line[prev_comma + 1:match_start].strip()
    words = segment.split()
    if not words or len(words) > 4:
        return False
    return words[0].lower() not in CLAUSE_OPENERS


def sweep_file(path: Path, cobalt_mode: bool, skills_marker: str):
    text = path.read_text(encoding="utf-8")
    fails, reports = [], []

    hits = MATH_ALNUM_RE.findall(text)
    if hits:
        fails.append(f"U+1D400-block chars: {len(hits)} ({''.join(sorted(set(hits))[:10])})")

    pua = PUA_RE.findall(text)
    if pua:
        # F97: tabulate per codepoint, never in aggregate -- the tail is where
        # meaning lives (61 content glyphs hid behind 2360 benign checkboxes)
        by_cp = {}
        for ch in pua:
            by_cp[ch] = by_cp.get(ch, 0) + 1
        table = ", ".join(f"U+{ord(c):04X} x{n}" for c, n in sorted(by_cp.items()))
        fails.append(f"Private Use Area chars (F97 -- invisible symbol-font glyphs; "
                     f"strip 0xF000 and read as Adobe Symbol to identify): {table}")

    n_escaped = text.count(chr(92) + "*")
    if n_escaped:
        fails.append(f"escaped starred refs (backslash-asterisk): {n_escaped}")

    # Round 12: the \Delta check below cites the ruling that ALSO bans U+0394,
    # but only tested the LaTeX form -- a gate that names a rule in its message
    # without testing it is documentation, not a gate (same lesson as F102).
    # Lower-case delta U+03B4 is unaffected (infinitesimals stay LaTeX \delta).
    n_greekcap = text.count("Δ")
    if n_greekcap:
        fails.append(f"bare U+0394 GREEK CAPITAL DELTA: {n_greekcap} (look-alike of the mandated "
                     f"U+2206 increment; Katie's Cobalt render test, 7 Aug 2026: U+0394 does not "
                     f"render -- normalise to U+2206)")

    for token, label in ((r"\Delta", r"\Delta (use Unicode increment U+2206 -- Katie's Cobalt render "
                          r"test, 7 Aug 2026: only U+2206 renders; U+0394 and \Delta both break. "
                          r"A rendering rule, not a semantic one -- do not re-litigate from Unicode "
                          r"block names, see F67 withdrawn)"),
                         ("$c{", "RN commentary syntax $c{"),
                         ("![", "image embed"),
                         ("http://", "http link"), ("https://", "https link")):
        n = text.count(token)
        if n:
            fails.append(f"{label}: {n}")

    if cobalt_mode:
        if "[!" in text:
            fails.append(f"callout marker [!: {text.count('[!')}")
        n_bq = sum(1 for ln in text.splitlines() if ln.startswith(">"))
        if n_bq:
            fails.append(f"blockquote lines: {n_bq}")
        # F71: check the strip's OUTPUT, not just for its non-occurrence.
        # F70 shipped 227 empty/parenthetical-only headings through this very
        # gate -- it checked for surviving "> " markers (strip didn't happen)
        # and never for what a completed strip had destroyed
        n_empty = sum(1 for ln in text.splitlines() if re.match(r"^#{1,6}\s*$", ln))
        if n_empty:
            fails.append(f"empty headings (a callout lost its title -- F70): {n_empty}")
        n_paren = sum(1 for ln in text.splitlines() if re.match(r"^#{1,6}\s+\(", ln))
        if n_paren:
            fails.append(f"headings that are only a parenthetical (callout title was empty -- F70): {n_paren}")

    for i, line in enumerate(text.splitlines(), 1):
        for m in OXFORD_RE.finditer(line):
            if looks_like_list(line, m.start()):
                reports.append(f"L{i} Oxford-comma candidate: ...{line[max(0, m.start() - 40):m.end() + 20].strip()}...")
        for m in CLAIM_RE.finditer(line):
            reports.append(f"L{i} unverified-claim vocabulary (F109/F111 -- needs an adjacent "
                           f"routes-tried list): ...{line[max(0, m.start() - 30):m.end() + 40].strip()}...")
        for m in QUANTIFIER_RE.finditer(line):
            reports.append(f"L{i} unbounded quantifier (F120 -- verify against an enumerated "
                           f"list or re-scope): ...{line[max(0, m.start() - 30):m.end() + 40].strip()}...")

    # F150: worked-example provenance, scoped per example BLOCK (label line to
    # the next heading or next label) -- never a fixed line window, which
    # counts neighbouring prose's references and clears unchecked content
    lines = text.splitlines()
    label_idx = [i for i, ln in enumerate(lines) if WE_LABEL_RE.search(ln)]
    for n, i in enumerate(label_idx):
        end = len(lines)
        for j in range(i + 1, len(lines)):
            if re.match(r"^#{1,6}\s", lines[j]) or WE_LABEL_RE.search(lines[j]):
                end = j
                break
        block = "\n".join(lines[i:end])
        if not PAPER_REF_RE.search(block):
            reports.append(f"L{i + 1} worked example with NO paper reference in its block "
                           f"(F150 -- rebuild from a named scheme or delete; never retrofit "
                           f"an attribution): {lines[i].strip()[:100]}")

    sp = len(re.findall(r"^## Spec Point:", text, re.M))
    kt = text.count("**Key terminology:**")
    sk = text.count(skills_marker)
    parity = f"SP={sp} KT={kt} SK={sk}"
    if sp != kt:
        fails.append(f"flag-block parity broken: {parity} (SP must equal KT)")

    return fails, reports, (sp, kt, sk)


def main() -> None:
    argv = sys.argv[1:]
    cobalt_mode = "--cobalt" in argv
    argv = [a for a in argv if a != "--cobalt"]
    skills_label = "Mathematical skills"
    if "--skills-label" in argv:
        i = argv.index("--skills-label")
        skills_label = argv[i + 1]
        del argv[i:i + 2]
    skills_marker = f"**{skills_label}:**"

    files = []
    for a in argv:
        p = Path(a)
        if p.is_dir():
            # F69: recursive by rule -- a non-recursive glob on a parent dir
            # (e.g. knowledge-files/ with unit subdirs) swept nothing and
            # reported a clean wave
            if cobalt_mode:
                files += sorted(p.rglob("*.cobalt.md"))
            else:
                files += sorted(f for f in p.rglob("*.md") if not f.name.endswith(".cobalt.md"))
        else:
            files.append(p)

    if not files:
        # F69: a gate that swept zero files must not report clean -- "0 files
        # swept" with exit 0 is indistinguishable from a passing sweep
        print("GATE COULD NOT RUN: no files matched the given paths"
              f" ({'*.cobalt.md' if cobalt_mode else '*.md'} mode) -- nothing was swept.")
        sys.exit(2)

    any_fail = False
    tot_sp = tot_kt = tot_sk = 0
    for f in files:
        fails, reports, (sp, kt, sk) = sweep_file(f, cobalt_mode, skills_marker)
        tot_sp, tot_kt, tot_sk = tot_sp + sp, tot_kt + kt, tot_sk + sk
        if fails or reports:
            print(f"\n== {f.name}")
            for x in fails:
                any_fail = True
                print(f"  FAIL  {x}")
            for x in reports:
                print(f"  check {x}")

    print(f"\n{len(files)} files swept ({'cobalt' if cobalt_mode else 'master'} mode). "
          f"Totals: SP={tot_sp} KT={tot_kt} SK({skills_label})={tot_sk}")
    print("Validate the skills-line total against the wave's OWN skills-omission ruling list "
          "(never a handover's stated expectation).")
    sys.exit(1 if any_fail else 0)


if __name__ == "__main__":
    main()
