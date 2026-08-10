#!/usr/bin/env python3
"""MS row-coverage check: reconcile each mark scheme's per-question rows
against its question paper's "Total for Question N" lines.

WHY (2026-08-10 feedback, 4PH1 wave 1): the converter's pipe-count table gate
passes a mark scheme that lost SINGLE rows or cells -- the table still parses,
the pipe count is healthy, and a marking point is gone. 10+ verified instances
in one wave. The QP prints an independent ground truth ("Total for Question 3
= 6 marks"), so per-question coverage is mechanically checkable.

WHAT IT CHECKS, per QP/MS pair (same directory, same stem minus the doc-type
token):
  1. COVERAGE (gate, exit 1): every question the QP totals must have at least
     one MS table row. A totalled question with zero MS rows is dropped
     content, full stop.
  2. MARK TALLY (report-only): where the MS mark column parses, a per-question
     tally below the QP total is a suspected partial row loss. Report-only
     because mark-column formats vary; a shortfall is a lead, not a verdict --
     read the MS against the PDF before acting on it.

A run that pairs nothing, or whose QPs yield zero totals, EXITS 2: a gate that
processed nothing has failed, not passed (F63/F69). Boards phrase totals
differently -- override --total-pattern (named groups 'q' and 'marks').

Usage:
  python ms_row_coverage.py ROOT
  python ms_row_coverage.py ROOT --total-pattern "Total for Question (?P<q>\\d+)\\s*[=:]\\s*(?P<marks>\\d+)"

Writes ms-row-coverage-report.json at ROOT.
"""
import argparse
import json
import os
import re
import sys

DEFAULT_MS_PATTERN = r"mark[\s_-]*scheme|\b(r?ms|msc)\b|[\s_-](r?ms|msc)[\s_.-]"
DEFAULT_QP_PATTERN = r"question[\s_-]*paper|\bqp\b|[\s_-]qp[\s_.-]"
DEFAULT_TOTAL_PATTERN = r"Total for Question\s*(?P<q>\d+)\s*[=:]?\s*(?P<marks>\d+)\s*marks?"

# First cell of an MS row opening a question block: "1", "1(a)", "1 (b)(ii)", "1."
ROW_QUESTION = re.compile(r"^\s*(\d{1,2})\s*[.(]?")
# A mark value in the mark column: "(1)", "1", "B1", "M1", "A1", "C1"
MARK_CELL = re.compile(r"^\s*\(?\s*(?:[BMAC]\s*)?(\d{1,2})\s*\)?\s*$")


def log(msg):
    print(msg, flush=True)


def find_mds(root):
    out = []
    for dirpath, _, files in os.walk(root):
        for fn in files:
            if fn.lower().endswith(".md"):
                out.append(os.path.join(dirpath, fn))
    return sorted(out)


def pair_key(path, ms_re, qp_re):
    """Directory + stem with the doc-type token removed, whitespace/case
    normalised -- '2024 June 1F Question paper' and '2024 June 1F Mark scheme'
    in one directory pair up."""
    stem = os.path.splitext(os.path.basename(path))[0]
    stem = ms_re.sub(" ", stem)
    stem = qp_re.sub(" ", stem)
    stem = re.sub(r"\s+", " ", stem).strip().lower()
    return (os.path.dirname(path), stem)


def qp_totals(text, total_re):
    """{question_number: total_marks} from the QP's printed totals. The LAST
    occurrence wins if a total is printed twice (e.g. contents + in place)."""
    totals = {}
    for m in total_re.finditer(text):
        totals[int(m.group("q"))] = int(m.group("marks"))
    return totals


def ms_rows_by_question(text):
    """Attribute MS table rows to main question numbers.

    MS tables label only the FIRST row of a question's block; following rows
    leave the question cell blank. Track the current question; a first cell
    opening with a new integer switches to it. Returns
    {q: {"rows": n, "marks": tally}} -- marks is 0 when the column never parsed.
    """
    per_q = {}
    current = None
    for line in text.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cells or all(not c for c in cells):
            continue
        # skip header/separator rows
        if re.match(r"^:?-{2,}:?$", cells[0]) or "question" in cells[0].lower():
            continue
        m = ROW_QUESTION.match(cells[0])
        if m:
            current = int(m.group(1))
        if current is None:
            continue
        entry = per_q.setdefault(current, {"rows": 0, "marks": 0})
        entry["rows"] += 1
        mk = MARK_CELL.match(cells[-1]) if cells[-1] else None
        if mk:
            entry["marks"] += int(mk.group(1))
    return per_q


def main():
    ap = argparse.ArgumentParser(description="Reconcile MS per-question rows against QP totals (Project Hero).")
    ap.add_argument("root", help="corpus root holding converted .md files")
    ap.add_argument("--ms-pattern", default=DEFAULT_MS_PATTERN)
    ap.add_argument("--qp-pattern", default=DEFAULT_QP_PATTERN)
    ap.add_argument("--total-pattern", default=DEFAULT_TOTAL_PATTERN,
                    help="regex with named groups 'q' and 'marks' matching the QP's per-question total lines")
    args = ap.parse_args()

    if not os.path.isdir(args.root):
        log(f"ROOT is not a directory: {args.root}")
        return 2
    ms_re = re.compile(args.ms_pattern, re.I)
    qp_re = re.compile(args.qp_pattern, re.I)
    total_re = re.compile(args.total_pattern, re.I)

    qps, mss = {}, {}
    for p in find_mds(args.root):
        base = os.path.basename(p)
        if ms_re.search(base):
            mss[pair_key(p, ms_re, qp_re)] = p
        elif qp_re.search(base):
            qps[pair_key(p, ms_re, qp_re)] = p

    pairs = sorted(set(qps) & set(mss))
    if not pairs:
        log(f"GATE COULD NOT RUN: no QP/MS pairs found under {args.root} "
            f"({len(qps)} QPs, {len(mss)} MSs recognised, none share a directory+stem).")
        log("Check --ms-pattern / --qp-pattern against this board's filenames.")
        return 2

    results, missing_total, shortfall_total, totals_seen = [], 0, 0, 0
    for key in pairs:
        qp_path, ms_path = qps[key], mss[key]
        qp_text = open(qp_path, encoding="utf-8", errors="replace").read()
        ms_text = open(ms_path, encoding="utf-8", errors="replace").read()
        totals = qp_totals(qp_text, total_re)
        rec = {
            "qp": os.path.relpath(qp_path, args.root),
            "ms": os.path.relpath(ms_path, args.root),
            "qp_questions_totalled": len(totals),
            "missing_questions": [],
            "tally_shortfalls": [],
        }
        if not totals:
            rec["note"] = "QP printed no parseable totals -- pair skipped (check --total-pattern)"
            results.append(rec)
            continue
        totals_seen += len(totals)
        per_q = ms_rows_by_question(ms_text)
        for q, marks in sorted(totals.items()):
            got = per_q.get(q)
            if not got or got["rows"] == 0:
                rec["missing_questions"].append({"question": q, "qp_marks": marks})
            elif 0 < got["marks"] < marks:
                rec["tally_shortfalls"].append(
                    {"question": q, "qp_marks": marks, "ms_mark_tally": got["marks"], "ms_rows": got["rows"]})
        missing_total += len(rec["missing_questions"])
        shortfall_total += len(rec["tally_shortfalls"])
        results.append(rec)

    if totals_seen == 0:
        log(f"GATE COULD NOT RUN: {len(pairs)} QP/MS pair(s) found but no QP yielded a single")
        log(f"parseable per-question total. This board phrases totals differently --")
        log(f"pass --total-pattern (current: {args.total_pattern!r}).")
        return 2

    log(f"{len(pairs)} QP/MS pair(s), {totals_seen} totalled questions reconciled.\n")
    for rec in results:
        if rec.get("note"):
            log(f"SKIPPED  {rec['qp']}: {rec['note']}")
        for m in rec["missing_questions"]:
            log(f"MISSING  {rec['ms']}: Question {m['question']} ({m['qp_marks']} marks in the QP) "
                f"has ZERO mark-scheme rows -- dropped content")
        for s in rec["tally_shortfalls"]:
            log(f"SHORTFALL  {rec['ms']}: Question {s['question']} tallies {s['ms_mark_tally']} of "
                f"{s['qp_marks']} QP marks over {s['ms_rows']} row(s) -- suspected partial row loss, "
                f"read against the PDF")

    out = os.path.join(args.root, "ms-row-coverage-report.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"pairs": len(pairs), "questions_reconciled": totals_seen,
                   "missing_questions": missing_total, "tally_shortfalls": shortfall_total,
                   "results": results}, f, indent=2)
    log(f"\nReport: {out}")

    if missing_total:
        log(f"\nROW-COVERAGE GATE FAILED: {missing_total} totalled question(s) with zero MS rows.")
        return 1
    log(f"\nROW-COVERAGE GATE PASSED ({shortfall_total} report-only tally shortfall(s) to eyeball).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
