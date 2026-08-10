"""Spec coverage gate — proves every spec statement is covered in full.

PACK PROVENANCE: written and production-tested by Leander Oates on 1PH0
(found: a Core Practical absent from the tracker entirely, a typo'd id making
one statement unreachable, and a wrong whole-statement tier flag). Imported
into the pack 7 Aug 2026; course-parameterised 10 Aug 2026 after a second
course needed a text-keyed rewrite of the hard-coded tracker shape.

PER-COURSE CONFIGURATION (project.json -> spec_coverage; defaults reproduce
1PH0 -- assert your denominator, F59):
  "spec_coverage": {
    "statement_id_regex": "\\d{1,2}\\.\\d{1,2}[PH]?",   # Edexcel GCSE grammar
    "tracker": {
      "first_data_row": 2,                # 0-based; rows above hold headers
      "definition_col": "Definition",     # header text (unique substring,
      "subtopic_col": "Subtopic",         #   matched case-insensitively in the
      "higher_tier_col": "Higher Tier"    #   header rows) OR a 0-based index.
    }                                     # higher_tier_col: null = untiered course
  }
After changing the id regex, check the parsed statement count against the
tracker's total. paths.specification_pdf should be set in project.json (F60);
the reference-dir glob is only a fallback.
Checks A/B run at /hero-0-setup §6 (setup-time); checks C/D gate
/hero-4-publish (blocking).

Three sources, three different jobs:
  tracker-master-syllabus.csv col 4  -> ALLOCATION (which Cobalt subtopic owns a statement)
  <course> - Specification.pdf       -> TEXT (verbatim wording, and bold = Higher Tier)
  knowledge-files/**.md              -> COVERAGE (what was actually written)

A statement may be split across several knowledge files (2.23's equilibrium and
collision halves) or several statements merged into one file, so coverage is
tested as a UNION over every file quoting that statement, never file by file.

Usage: python3 scripts/spec_coverage_gate.py [--pdf-cache PATH]
Exit 1 if any statement is written but incomplete, or allocated but unfindable.
"""
import csv, json, re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
CFG = json.loads((ROOT / "project.json").read_text(encoding="utf-8"))
SPEC_CFG = CFG.get("spec_coverage") or {}
TRK_CFG = SPEC_CFG.get("tracker") or {}
ID = re.compile(SPEC_CFG.get("statement_id_regex") or r"\d{1,2}\.\d{1,2}[PH]?")


def resolve_col(spec, header_rows, default_idx, what):
    """A column is named by header text (unique case-insensitive substring
    across the header rows) or given as a 0-based index. Ambiguity and misses
    FAIL LOUDLY -- a wrong column read silently was exactly the 1PH0 hazard."""
    if spec is None:
        return default_idx
    if isinstance(spec, int):
        return spec
    hits = set()
    for row in header_rows:
        for i, cell in enumerate(row):
            if spec.lower() in cell.strip().lower():
                hits.add(i)
    if len(hits) != 1:
        sys.exit(f"tracker column {what!r}: header text {spec!r} matched "
                 f"{len(hits)} column(s) in the header rows -- fix "
                 f"project.json -> spec_coverage.tracker ({sorted(hits) or 'no match'})")
    return hits.pop()


def norm(s):
    s = re.sub(r"\[[^\]]*\]", " ", s)          # drop dated repair notes
    s = re.sub(r"<[^>]+>|\*\*|_", " ", s)      # <sup>/<br> etc are layout, not content
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def blob(s):
    return norm(s).replace(" ", "")


def pdf_statements(md):
    """id -> (text, higher_tier). Bold spans in the PDF mark Higher Tier content."""
    out = {}
    for line in md.split("\n"):
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cells:
            continue
        # Cell 0 is normally the bare id, but the PDF's own table extraction
        # sometimes fuses id and statement into one cell (15.13P-15.17P) — take
        # the remainder of that cell as the statement text when it does.
        # Only consume a trailing ** if the id itself was bolded, else
        # `|15.13P**Explain why...` loses the bold span that opens the statement.
        m = re.match(r"(\*\*)?(" + ID.pattern + r")(\*\*)?\s*(.*)$", cells[0])
        if not m or bool(m.group(1)) != bool(m.group(3)):
            m = re.match(r"(\*\*)?(" + ID.pattern + r")()\s*(.*)$", cells[0])
        if not m:
            continue
        raw = m.group(4).strip() or (cells[1] if len(cells) > 1 else "")
        if not raw:
            continue
        out.setdefault(m.group(2), (raw, bold_extent(raw)))
    return out


def bold_extent(raw):
    """none / partial / all. A PARTIAL statement is Higher Tier for only part of
    itself, which is why the tracker gives it two subtopic homes."""
    bold = len(blob("".join(re.findall(r"\*\*(.+?)\*\*", raw))))
    total = len(blob(raw))
    if not bold or not total:
        return "none"
    return "all" if bold / total > 0.9 else "partial"


def tracker_allocation(path):
    """id -> [(subtopic, higher_tier)], from the tracker's definition column.
    Columns and first data row come from project.json -> spec_coverage.tracker
    (defaults: the 1PH0 Master Syllabus layout -- definition col 4, subtopic
    col 2, Higher-Tier col 5, data from row 3). Beware abridged duplicate
    listings in other columns (1PH0 col 9 duplicated 12.4) -- point
    definition_col at the authoritative one only.

    A statement can appear against SEVERAL subtopics. That is not duplication:
    it is how the tracker splits a statement whose halves sit in different
    subtopics, or on different tiers (2.23 equilibrium/collision,
    4.10 direction/speed). The list is the statement's full allocation."""
    alloc = {}
    rows = list(csv.reader(open(path, encoding="utf-8-sig")))
    first_data = TRK_CFG.get("first_data_row", 2)
    headers = rows[:first_data]
    def_col = resolve_col(TRK_CFG.get("definition_col"), headers, 4, "definition_col")
    sub_col = resolve_col(TRK_CFG.get("subtopic_col"), headers, 2, "subtopic_col")
    ht_spec = TRK_CFG.get("higher_tier_col", 5)  # explicit null = untiered course
    ht_col = None if ht_spec is None else resolve_col(ht_spec, headers, 5, "higher_tier_col")
    needed = max(def_col, sub_col, ht_col if ht_col is not None else 0) + 1
    pat = re.compile(r"(?m)(?:^|(?<=\n))\s*(" + ID.pattern + r")\s+")
    for r in rows[first_data:]:
        if len(r) < needed or not r[def_col].strip():
            continue
        for m in pat.finditer(r[def_col].replace("\r", "")):
            homes = alloc.setdefault(m.group(1), [])
            entry = (r[sub_col].strip(), bool(r[ht_col].strip()) if ht_col is not None else False)
            if entry not in homes:
                homes.append(entry)
    return alloc


def written_quotes(kdir):
    """id -> [(file, quoted text)].

    A quote block is `> **Specification:** <id> <text>`, but a block may carry
    FURTHER statements on bare continuation lines (`> 2.2 Explain that...`).
    Reading only the header line silently under-counts what was written."""
    q = {}
    head = re.compile(r"^>\s*\*\*Specification:\*\*\s*(" + ID.pattern + r")\s+(.*)$")
    cont = re.compile(r"^>\s*(" + ID.pattern + r")\s+(.*)$")
    for f in sorted(pathlib.Path(kdir).rglob("*.md")):
        inblock = False
        for line in f.read_text(encoding="utf-8").split("\n"):
            m = head.match(line) or (cont.match(line) if inblock else None)
            inblock = bool(m) or (inblock and line.startswith(">"))
            if m:
                q.setdefault(m.group(1), []).append((f.name, m.group(2)))
    return q


def uncovered(pdf_text, quotes):
    """PDF tokens absent from the union of quotes. Substring-matched against a
    despaced blob so the PDF's glyph fusion (`lawbothto`) and the conversion's
    word splitting (`13 C`) both pass."""
    hay = "".join(blob(t) for _, t in quotes)
    return [t for t in norm(pdf_text).split() if len(t) >= 3 and t not in hay]


def main():
    cache = pathlib.Path(sys.argv[sys.argv.index("--pdf-cache") + 1]) if "--pdf-cache" in sys.argv else None
    if cache and cache.exists():
        md = cache.read_text(encoding="utf-8")
    else:
        import pymupdf4llm
        # project.json has no specification_pdf key (F60) — fall back to the reference dir
        pdf_path = CFG["paths"].get("specification_pdf") or next(iter(
            sorted((ROOT / "research" / "reference").glob("*Specification*.pdf"))))
        md = pymupdf4llm.to_markdown(str(ROOT / pdf_path), show_progress=False)
        if cache:
            cache.write_text(md, encoding="utf-8")

    pdf = pdf_statements(md)
    alloc = tracker_allocation(ROOT / CFG["paths"]["syllabus_cross_check"])
    quotes = written_quotes(ROOT / "knowledge-files")
    order = lambda x: [int(n) for n in re.findall(r"\d+", x)]

    print(f"PDF statements: {len(pdf)}   tracker statements: {len(alloc)}   written: {len(quotes)}\n")
    fail = 0

    print("== A. Allocation — every statement exists in both sources and has a subtopic home ==")
    only_trk, only_pdf = sorted(set(alloc) - set(pdf), key=order), sorted(set(pdf) - set(alloc), key=order)
    if only_trk:
        print(f"  FAIL  in tracker, absent from the PDF — check for a typo'd id ({len(only_trk)}): {only_trk}")
    if only_pdf:
        print(f"  FAIL  in the PDF, no tracker subtopic — nothing on site owns these ({len(only_pdf)}):")
        for sid in only_pdf:
            print(f"          {sid}  {norm(pdf[sid][0])[:88]}")
    fail += bool(only_trk) + bool(only_pdf)
    if not (only_trk or only_pdf):
        print("  PASS  both sources carry the same statement set")

    print("\n== B. Split statements — partly Higher Tier, so the tracker splits them across subtopics ==")
    for sid in sorted(set(pdf) & set(alloc), key=order):
        extent, homes = pdf[sid][1], alloc[sid]
        ht = [h for h, t in homes if t]
        if extent == "partial":
            if len(homes) < 2 or not ht or len(ht) == len(homes):
                print(f"  FAIL  {sid} is partly bold in the PDF but the tracker does not split it: {homes}")
                fail += 1
            else:
                print(f"  SPLIT {sid}  core -> {[h for h, t in homes if not t]}   HT -> {ht}")
        elif extent == "all" and not all(t for _, t in homes):
            print(f"  FAIL  {sid} is wholly Higher Tier in the PDF, tracker says otherwise: {homes}")
            fail += 1
        elif extent == "none" and ht:
            print(f"  FAIL  {sid} is not bold in the PDF, tracker flags Higher Tier: {homes}")
            fail += 1

    print("\n== C. Coverage — is each written statement covered IN FULL, unioned across files ==")
    incomplete = []
    for sid in sorted(quotes, key=order):
        if sid not in pdf:
            print(f"  FAIL  {sid} quoted in {quotes[sid][0][0]} but not found in the PDF")
            fail += 1
            continue
        miss = uncovered(pdf[sid][0], quotes[sid])
        if miss:
            incomplete.append((sid, miss, [f for f, _ in quotes[sid]]))
    for sid, miss, files in incomplete:
        print(f"  FAIL  {sid} incomplete — the PDF says {miss}, no file covers it")
        print(f"        written in: {', '.join(sorted(set(files)))}")
        print(f"        allocated to: {[h for h, _ in alloc.get(sid, [])]}")
    if not incomplete:
        print(f"  PASS  all {len(quotes)} written statements covered in full")
    fail += len(incomplete)

    print("\n== D. Not yet written (informational — expected until the last wave) ==")
    todo = sorted(set(alloc) - set(quotes), key=order)
    subs = {h for sid in todo for h, _ in alloc[sid]}
    part = [sid for sid in todo if any(h in {x for s in quotes for x, _ in alloc.get(s, [])} for h, _ in alloc[sid])]
    print(f"  {len(todo)} statements across {len(subs)} subtopics remain unwritten")
    # The wave-completeness proof: a statement allocated to a subtopic that HAS
    # been written, but quoted nowhere, is a hole in delivered work — not backlog.
    if part:
        print(f"  FAIL  {len(part)} sit in a subtopic already written but are quoted nowhere: {part}")
        fail += len(part)
    else:
        print("  PASS  every statement allocated to an already-written subtopic is written")

    print(f"\n{'GATE FAILED' if fail else 'GATE PASSED'}")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
