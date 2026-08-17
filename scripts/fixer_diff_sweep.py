"""Mechanical re-sweep of fixer output.

Why: in the pilot build, one live defect (a false "the answer is X every
time" claim) was INTRODUCED by a fixer's own fix text after the checker signed
off. Nothing re-checked fixer output. This script closes that gap cheaply: it
scans only the lines the fixer ADDED (via git diff) for the two failure classes
a fixer can introduce:

  1. Manufactured-certainty patterns (CHECKER.md rules 15/16): absolutes,
     superlatives, frequency claims, invented concessions
  2. New quoted spans — every quotation mark a fixer adds is a quote-integrity
     risk (paraphrase-in-quotes was a recurring blocker class)

Report-only on HITS: hits are candidates for orchestrator eyeballing, not
auto-fails. A hit means "read this changed line before stripping", nothing more.

NOT report-only on RUNNABILITY (F63): a file outside a git repository, or not
tracked, has no baseline to diff -- the sweep inspects nothing. That case exits
non-zero and prints GATE COULD NOT RUN, never "clean". On 1PH0 this script
printed "fixer diff clean" on every fixer-touched file of a whole build because
/hero-0-setup had never run `git init` -- the gate was decorative from setup,
and the one residue it existed to catch had to be found by hand. Silence and
success must not look alike.

Usage:
  python fixer_diff_sweep.py <file.md> [more files...]     # vs HEAD
  python fixer_diff_sweep.py --ref <git-ref> <file.md> ...  # vs given ref

Run AFTER the fixer, BEFORE strip_for_cobalt.py, while the pre-fixer version
is still what git HEAD (or --ref) holds. Exit codes: 0 = swept (hits or not),
2 = GATE COULD NOT RUN on at least one file (step 4 is NOT satisfied).
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

CERTAINTY_PATTERNS = [
    # 'every' is generalised to ANY following word (17 Aug 2026, 1PH0 wave 3):
    # the old enumerated list (question|paper|scheme|year) let a fixer-introduced
    # "Every difference in that bank is worded as a comparison" through as clean,
    # because "difference" was not on the list -- a gate that enumerates the words
    # it looks for measures its own vocabulary. The generalised form is far
    # noisier (~56 hits a wave on 1PH0, mostly correct bounded forms like "every
    # one of the seven schemes") and that is the right trade: a false positive
    # costs a glance, a miss ships a claim.
    (r"\balways\b", "absolute: 'always'"),
    (r"\bnever\b", "absolute: 'never'"),
    (r"\bevery\s+\w+", "quantifier: 'every <anything>'"),
    (r"\balmost (?:every|all)\b", "frequency: 'almost every/all'"),
    (r"\bmost (?:common|often|frequently|heavily|reused)\b", "superlative: 'most ...'"),
    (r"\bthe (?:single )?(?:most|biggest|commonest|dominant)\b", "superlative"),
    (r"\bin any sitting\b", "frequency: 'in any sitting'"),
    (r"\bguarantee[sd]?\b", "concession: 'guarantee'"),
    (r"\bbanks? (?:a|the|one) mark\b", "concession: 'banks a mark'"),
    (r"\bstill (?:earns?|scores?|gets?)\b", "concession: 'still earns/scores'"),
    (r"\bforfeits?\b", "rejection: 'forfeits'"),
    (r"\bnot (?:be )?(?:credited|accepted)\b", "rejection rule"),
    (r"\bexaminers (?:always|never|reject|require)\b", "invented examiner rule"),
    (r"\bwould also be accepted\b", "equivalence claim"),
    (r"[\"“”]", "new quoted span — verify verbatim against the pack"),
]

# Falsification cases carried AS CODE (17 Aug 2026, from the 1PH0 tier-sweep
# rebuild): a gate whose detector drifts must refuse to run, never sweep and
# report clean. Each case is (line, must_hit). The first is the real fixer
# regression the enumerated-noun pattern missed in production.
SELF_TEST = [
    ("Every difference in that bank is worded as a comparison", True),
    ("every scheme on this course rewards the substitution first", True),
    ("This route always earns the second mark", True),
    ("Examiners never accept a bare number here", True),
    ("The gradient of a velocity-time graph gives the acceleration", False),
    ("Work the error through once and check the direction", False),
]


def selftest_failures():
    """Return the SELF_TEST cases the current patterns get wrong (empty = pass)."""
    fails = []
    for line, must_hit in SELF_TEST:
        hit = any(re.search(pat, line, re.IGNORECASE) for pat, _ in CERTAINTY_PATTERNS)
        if hit != must_hit:
            fails.append((line, must_hit))
    return fails


def baseline_exists(path: Path) -> bool:
    """True only when git can actually supply a pre-fixer baseline for path.

    False means the sweep CANNOT run for this file — not that it is clean.
    Covers both failure shapes seen in production (F63): no repository at all
    (hero-0-setup historically never ran `git init`), and a file never
    committed, so the diff is empty however much the fixer changed."""
    in_repo = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        capture_output=True, text=True, cwd=path.parent, encoding="utf-8",
    ).returncode == 0
    if not in_repo:
        return False
    return subprocess.run(
        ["git", "ls-files", "--error-unmatch", path.name],
        capture_output=True, text=True, cwd=path.parent, encoding="utf-8",
    ).returncode == 0


def added_lines(path: Path, ref: str):
    path = path.resolve()
    out = subprocess.run(
        ["git", "diff", "-U0", ref, "--", path.name],
        capture_output=True, text=True, cwd=path.parent, encoding="utf-8",
    ).stdout
    lineno = None
    for raw in out.splitlines():
        m = re.match(r"^@@ -\d+(?:,\d+)? \+(\d+)", raw)
        if m:
            lineno = int(m.group(1))
            continue
        if lineno is None:
            continue
        if raw.startswith("+") and not raw.startswith("+++"):
            yield lineno, raw[1:]
            lineno += 1


def main() -> None:
    # Swept lines carry source glyphs a cp1252 console cannot encode — U+2212
    # crashed the whole sweep in production (2026-08-10). Reconfigure rather
    # than depending on every caller remembering PYTHONIOENCODING=utf-8.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    ap = argparse.ArgumentParser(
        description="Scan the lines a fixer ADDED (git diff vs a ref) for "
        "manufactured-certainty patterns and new quoted spans. Report-only.",
    )
    ap.add_argument("--ref", default="HEAD", help="git ref to diff against (default: HEAD)")
    ap.add_argument("files", nargs="+", metavar="file.md", help="fixer-touched files to sweep")
    ns = ap.parse_args()
    ref = ns.ref

    bad = selftest_failures()
    if bad:
        print("GATE COULD NOT RUN: pattern self-test failed — the detector no "
              "longer catches (or wrongly fires on) its own falsification cases:")
        for line, must_hit in bad:
            print(f"  {'MUST-HIT missed' if must_hit else 'MUST-PASS fired'}: {line}")
        print("Fix CERTAINTY_PATTERNS (and keep the failing case in SELF_TEST) "
              "before sweeping — a gate that fails its own self-test must not "
              "declare anything clean.")
        raise SystemExit(2)

    total_hits = 0
    unrunnable = []
    for a in ns.files:
        path = Path(a)
        if not baseline_exists(path.resolve()):
            # F63: never print "clean" for a file we could not inspect
            print(f"== {path.name} — GATE COULD NOT RUN: no git baseline "
                  f"(not in a repository, or never committed) — nothing was swept")
            unrunnable.append(path)
            continue
        hits = []
        for lineno, line in added_lines(path, ref):
            for pat, label in CERTAINTY_PATTERNS:
                if re.search(pat, line, re.IGNORECASE):
                    hits.append((lineno, label, line.strip()))
        if hits:
            print(f"\n== {path.name} — {len(hits)} changed-line hit(s) to eyeball")
            for lineno, label, text in hits:
                print(f"  L{lineno} [{label}]")
                print(f"      {text[:160]}")
            total_hits += len(hits)
        else:
            print(f"== {path.name} — fixer diff clean")

    if unrunnable:
        print(f"\nGATE COULD NOT RUN on {len(unrunnable)} file(s) — step 4 is NOT satisfied.")
        print("Fix: `git init` the project directory and commit the pre-fixer masters")
        print("(hero-0-setup does this on new projects), then re-run. A gate that")
        print("cannot see its input must fail loudly, never pass quietly.")
        raise SystemExit(2)
    print(f"\nDone. {total_hits} hit(s). Each is a read-before-strip candidate, not an auto-fail.")


if __name__ == "__main__":
    main()
