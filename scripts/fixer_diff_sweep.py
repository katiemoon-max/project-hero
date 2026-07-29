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

Report-only: hits are candidates for orchestrator eyeballing, not auto-fails.
A hit means "read this changed line before stripping", nothing more.

Usage:
  python fixer_diff_sweep.py <file.md> [more files...]     # vs HEAD
  python fixer_diff_sweep.py --ref <git-ref> <file.md> ...  # vs given ref

Run AFTER the fixer, BEFORE strip_for_cobalt.py, while the pre-fixer version
is still what git HEAD (or --ref) holds. Exit code is always 0.
"""

import argparse
import re
import subprocess
from pathlib import Path

CERTAINTY_PATTERNS = [
    (r"\bevery time\b", "absolute: 'every time'"),
    (r"\balways\b", "absolute: 'always'"),
    (r"\bnever\b", "absolute: 'never'"),
    (r"\bevery sitting\b", "frequency: 'every sitting'"),
    (r"\bevery (?:question|paper|scheme|year)\b", "frequency: 'every ...'"),
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


def added_lines(path: Path, ref: str):
    path = path.resolve()
    out = subprocess.run(
        ["git", "diff", "-U0", ref, "--", path.name],
        capture_output=True, text=True, cwd=path.parent, encoding="utf-8",
    ).stdout
    if not out.strip():
        # Distinguish "no changes" from "file unknown to git" — a silent empty
        # diff on an untracked/mistyped path would report a false "clean"
        tracked = subprocess.run(
            ["git", "ls-files", "--error-unmatch", path.name],
            capture_output=True, text=True, cwd=path.parent, encoding="utf-8",
        ).returncode == 0
        if not tracked:
            print(f"  WARNING: {path.name} is not tracked by git — diff is meaningless")
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
    ap = argparse.ArgumentParser(
        description="Scan the lines a fixer ADDED (git diff vs a ref) for "
        "manufactured-certainty patterns and new quoted spans. Report-only.",
    )
    ap.add_argument("--ref", default="HEAD", help="git ref to diff against (default: HEAD)")
    ap.add_argument("files", nargs="+", metavar="file.md", help="fixer-touched files to sweep")
    ns = ap.parse_args()
    ref = ns.ref

    total_hits = 0
    for a in ns.files:
        path = Path(a)
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

    print(f"\nDone. {total_hits} hit(s). Each is a read-before-strip candidate, not an auto-fail.")


if __name__ == "__main__":
    main()
