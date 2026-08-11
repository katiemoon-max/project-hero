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
    "statement_shapes": ["table"],        # add "prose" for specs whose converted
                                          #   md carries statements OUTSIDE tables:
                                          #   fused prose runs (1.3-1.10 on one
                                          #   line), bullets, picture-text blocks
                                          #   with <br> separators. Prose mode
                                          #   turns on a monotonic statement-id
                                          #   guard (decimals inside statement
                                          #   text are never taken as ids)
    "bounds": {"start_regex": null,       # optional line regexes bounding the
               "end_regex": null},        #   statement region (e.g. up to the
                                          #   appendix) -- prose mode wants these
    "unallocated_whitelist_regex": null,  # normalised statement texts matching
                                          #   this are SANCTIONED as unallocated
                                          #   (checks A/D) -- e.g. 4PH1's
                                          #   'use the following units?' ruling
    "tier_from_bold": true,               # false skips check B loudly, for
                                          #   courses whose tier source is not
                                          #   PDF bold (e.g. a P-suffix)
    "tracker": {
      "first_data_row": 2,                # 0-based; rows above hold headers
      "definition_col": "Definition",     # header text (unique substring,
      "subtopic_col": "Subtopic",         #   matched case-insensitively in the
      "higher_tier_col": "Higher Tier"    #   header rows) OR a 0-based index.
    }                                     # higher_tier_col: null = untiered course
  }
After changing the id regex, check the parsed statement count against the
tracker's total. paths.specification_pdf should be set in project.json (F60);
the reference-dir glob is only a fallback. Path fields read from project.json
must be PURE paths (2026-08-10): a glued human annotation inside
paths.syllabus_cross_check broke this gate's file open in production -- prose
about a path lives in a companion "<key>_note" field, and this script fails
loudly on a path value that does not resolve.

Courses whose tracker carries NO statement ids (text-keyed join) need more
than configuration -- see the 4PH1 build's spec_coverage_gate_4ph1.py for the
reference adaptation (containment + token-overlap join with a shortest-
statement specificity tie-break on split rows).
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


def cfg_path(key, required=True):
    """project.json path fields are PURE paths (2026-08-10): a human annotation
    glued into paths.syllabus_cross_check broke this gate's file open. Prose
    belongs in a companion '<key>_note' field; a path that does not resolve
    fails LOUDLY here, never as a bare FileNotFoundError deep in a parse."""
    raw = (CFG.get("paths") or {}).get(key)
    if raw is None:
        if required:
            sys.exit(f"project.json paths.{key} is missing -- the gate cannot run")
        return None
    if not isinstance(raw, str) or "\n" in raw or raw != raw.strip():
        sys.exit(f"project.json paths.{key} is not a PURE path: {raw!r} -- "
                 f"move any prose to paths.{key}_note")
    p = ROOT / raw
    if not p.exists():
        sys.exit(f"project.json paths.{key} does not resolve on disk: {p}\n"
                 f"If the value carries a glued annotation, paths are PURE "
                 f"(2026-08-10) -- move the prose to paths.{key}_note")
    return p


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


def split_row(line):
    """Cells of a markdown table row, splitting on EXACTLY ONE boundary pipe
    each side. str.strip('|') eats ALL leading pipes, deleting an empty first
    cell -- every continuation row orphans, statements truncate ('2.20 know
    that:'), and the truncated blobs become containment WILDCARDS that steal
    text-join allocations (9 misallocations from 2 truncations on 4PH1)."""
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in s.split("|")]


def pdf_statements(md):
    """id -> (text, higher_tier). Bold spans in the PDF mark Higher Tier content.

    Shapes handled (2026-08-10, folded back from the 4PH1 adaptation):
      - table rows, including id+statement fused into one cell
      - table CONTINUATION rows (empty first cell -> text continues the
        previous statement across rows)
      - with "prose" in spec_coverage.statement_shapes: fused prose runs
        (1.3-1.10 on one line), bullet lines, and picture-text blocks with
        <br> separators. Prose mode turns on a monotonic statement-id guard
        so decimals inside statement TEXT are never taken as statement ids.
    """
    shapes = SPEC_CFG.get("statement_shapes") or ["table"]
    prose = "prose" in shapes
    bounds = SPEC_CFG.get("bounds") or {}
    lines = md.split("\n")
    start, end = 0, len(lines)
    if bounds.get("start_regex"):
        pat = re.compile(bounds["start_regex"])
        start = next((i for i, ln in enumerate(lines) if pat.search(ln)), 0)
    if bounds.get("end_regex"):
        pat = re.compile(bounds["end_regex"])
        end = next((i for i, ln in enumerate(lines[start:], start) if pat.search(ln)), len(lines))

    prev = [0, 0]

    def accept(sid):
        """Monotonic-id guard (prose mode only): ids arrive in document order,
        stepping by at most 3 within a section or resetting to .1 in the next.
        Anything else is a decimal in statement text, not an id."""
        if not prose:
            return True
        nums = [int(n) for n in re.findall(r"\d+", sid)]
        if len(nums) < 2:
            return True
        m, n = nums[0], nums[1]
        ok = (m == prev[0] and prev[1] < n <= prev[1] + 3) or (m == prev[0] + 1 and n == 1)
        if ok:
            prev[0], prev[1] = m, n
        return ok

    out, last = {}, None
    idtok = re.compile(r"(?:(?<=\s)|^)\*{0,2}(" + ID.pattern + r")\*{0,2}(?=\s)")
    for line in lines[start:end]:
        if line.startswith("|"):
            cells = split_row(line)
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
            if m and m.group(2) not in out and accept(m.group(2)):
                raw = m.group(4).strip() or (cells[1] if len(cells) > 1 else "")
                if not raw:
                    continue
                out[m.group(2)] = (raw, bold_extent(raw))
                last = m.group(2)
            elif not cells[0] and last and any(cells[1:]) \
                    and not all(re.fullmatch(r":?-{2,}:?", c) for c in cells[1:] if c):
                # continuation row: empty id cell, statement text carries on
                raw = out[last][0] + " " + " ".join(c for c in cells[1:] if c)
                out[last] = (raw, bold_extent(raw))
            continue
        if not prose:
            continue
        # bullet / prose line — split the line at each accepted id token.
        # Picture-text blocks (4PH1 section 5(b)) use <br> separators;
        # normalise them to spaces or their ids are invisible to the tokenizer.
        ln = re.sub(r"<br\s*/?>", " ", line)
        hits = [(m2.start(1), m2.group(1)) for m2 in idtok.finditer(" " + ln)]
        kept = [(p, s) for p, s in hits if s not in out and accept(s)]
        for j, (p, s) in enumerate(kept):
            stop = kept[j + 1][0] if j + 1 < len(kept) else len(ln) + 1
            raw = (" " + ln)[p + len(s):stop].strip(" -_:")
            extent = bold_extent(raw)
            raw = re.sub(r"\*+", "", raw).strip()
            if raw:
                out[s] = (raw, extent)
                last = s
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
    # cp1252 consoles crash on source glyphs (U+2212 etc) in printed statement
    # text (2026-08-10) — reconfigure rather than requiring PYTHONIOENCODING
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    cache = pathlib.Path(sys.argv[sys.argv.index("--pdf-cache") + 1]) if "--pdf-cache" in sys.argv else None
    if cache and cache.exists():
        md = cache.read_text(encoding="utf-8")
    else:
        import pymupdf4llm
        # project.json has no specification_pdf key (F60) — fall back to the reference dir
        pdf_path = cfg_path("specification_pdf", required=False) or next(iter(
            sorted((ROOT / "research" / "reference").glob("*Specification*.pdf"))))
        md = pymupdf4llm.to_markdown(str(pdf_path), show_progress=False)
        if cache:
            cache.write_text(md, encoding="utf-8")

    pdf = pdf_statements(md)
    alloc = tracker_allocation(cfg_path("syllabus_cross_check"))
    quotes = written_quotes(ROOT / "knowledge-files")
    order = lambda x: [int(n) for n in re.findall(r"\d+", x)]

    # Ruling-sanctioned unallocated statements (e.g. 4PH1's ten 'use the
    # following units' rows, unallocated by user ruling 2026-08-07) — exempt
    # from checks A and D, never from C: once written, coverage still binds
    wl_pat = SPEC_CFG.get("unallocated_whitelist_regex")
    wl = {sid for sid, (t, _) in pdf.items()
          if wl_pat and re.match(wl_pat, norm(t), re.I)} if wl_pat else set()

    print(f"PDF statements: {len(pdf)}   tracker statements: {len(alloc)}   written: {len(quotes)}"
          + (f"   whitelisted-unallocated: {len(wl)}" if wl else "") + "\n")
    fail = 0

    print("== A. Allocation — every statement exists in both sources and has a subtopic home ==")
    only_trk = sorted(set(alloc) - set(pdf), key=order)
    only_pdf = sorted(set(pdf) - set(alloc) - wl, key=order)
    if only_trk:
        print(f"  FAIL  in tracker, absent from the PDF — check for a typo'd id ({len(only_trk)}): {only_trk}")
    if only_pdf:
        print(f"  FAIL  in the PDF, no tracker subtopic — nothing on site owns these ({len(only_pdf)}):")
        for sid in only_pdf:
            print(f"          {sid}  {norm(pdf[sid][0])[:88]}")
    fail += bool(only_trk) + bool(only_pdf)
    if not (only_trk or only_pdf):
        print("  PASS  both sources carry the same statement set"
              + (f" ({len(wl)} unallocated by whitelist ruling)" if wl else ""))

    print("\n== B. Split statements — partly Higher Tier, so the tracker splits them across subtopics ==")
    if SPEC_CFG.get("tier_from_bold") is False:
        # never silent: the skip is printed, and tier adjudication still owes
        # its answer at the course's declared tier source
        print("  SKIP  spec_coverage.tier_from_bold is false — this course's tier "
              "source is not PDF bold (see course.tier_source); adjudicate tier there")
    else:
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
    todo = sorted(set(alloc) - set(quotes) - wl, key=order)
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
