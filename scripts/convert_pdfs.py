#!/usr/bin/env python3
"""PDF -> Markdown converter for the Project Hero corpus (docling, table-aware).

Writes <name>.md next to each <name>.pdf under ROOT (recursive), one `## Page N`
section per PDF page so downstream page-anchored quoting keeps working.

WHY DOCLING AND NOT A TEXT-LAYER EXTRACTOR (finding F17, 1PH0, 31 July 2026):
mark schemes ARE tables. A flat reading-order extractor (`page.get_text("text")`)
discards table geometry, so question order scrambles, "Additional guidance" text
detaches from its marking point, mark allocations float unanchored, and symbol-font
glyphs degrade -- a minus sign silently vanished from an equation in the benchmark.
Every one of those failures is SILENT: the run reports success and the files look
plausible. R2 only ever sees this markdown, so a bad conversion reaches a writer
agent as wrong physics. Benchmarked on the same 30-page mark scheme: text-layer
28,100 chars / 0 table pipes, docling 69,682 chars / 829 pipes.

The TABLE-INTEGRITY GATE below is the guard: a mark scheme that converts to zero
pipe characters has no table left, and this script FAILS LOUDLY (exit 1) rather
than passing quietly.

Resumable: skips files already converted by THIS script (marker on line 1) and
overwrites .md produced by anything else -- including older text-layer runs -- so
a corpus upgrades in place on re-run. Flags docs with no extractable text (scans),
which need OCR or a PDF-direct fallback; record those in project.json ->
corpus.known_casualties.

This is the converter /hero-0-setup 5.1 kicks off. It is board- and subject-
agnostic: point it at the corpus root and it converts every PDF it finds.

Usage:
  python convert_pdfs.py ROOT                     # convert all PDFs under ROOT
  python convert_pdfs.py ROOT --subdir "Unit 1"   # only one subfolder of ROOT
  python convert_pdfs.py ROOT --limit 3           # smoke test on the first 3
  python convert_pdfs.py ROOT --verify            # audit existing .md, convert nothing
  python convert_pdfs.py ROOT --ms-pattern "ms|scheme"   # override MS detection

Writes conversion-report.json at ROOT (per-file chars/pages/pipes/tables + the
gate verdict) -- cite it when setting corpus.conversion.status in project.json.
A sharded run (--subdir/--limit) writes conversion-report--<scope>.json instead,
so a partial verdict can never be mistaken for the corpus-wide one.

Requires: pip install docling  (in scripts/requirements.txt). First run downloads
the layout + table-structure models (~500 MB, once per machine). Budget roughly
2-3 s per page on CPU (measured: 18-page mark scheme in 42 s) -- start the run
early, it is designed to work in the background while setup completes.
"""
import argparse
import json
import os
import re
import sys
import time
import traceback

MARKER = "<!-- docling-extract v1 -->"
PAGE_BREAK = "<!--__HERO_PAGE_BREAK__-->"

# Filenames matching this are mark schemes, and are held to the table-integrity
# gate. Covers the human-readable form and the board abbreviations seen so far
# (Edexcel ms/msc/rms, CIE _ms_). Override with --ms-pattern for anything else --
# check the hit list the run prints before trusting the gate on a new board.
DEFAULT_MS_PATTERN = r"mark[\s_-]*scheme|\b(r?ms|msc)\b|[\s_-](r?ms|msc)[\s_.-]"

NO_TEXT_CHARS = 200  # below this a doc is treated as a scan


def log(msg):
    print(msg, flush=True)


def build_converter():
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend

    opts = PdfPipelineOptions()
    opts.do_ocr = False                     # exam-board PDFs are digital -> skip OCR (much faster)
    opts.do_table_structure = True          # the whole point: recover mark-scheme tables
    opts.table_structure_options.do_cell_matching = True
    opts.do_formula_enrichment = False      # no benefit on inline exam maths, costs time
    # pypdfium backend avoids the std::bad_alloc page-drops seen with docling-parse
    return DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=opts, backend=PyPdfiumDocumentBackend
            )
        }
    )


def already_done(md_path):
    if not os.path.exists(md_path) or os.path.getsize(md_path) == 0:
        return False
    try:
        with open(md_path, "r", encoding="utf-8") as f:
            return f.readline().strip() == MARKER
    except Exception:
        return False


def paginate(body, stem):
    """Split docling's placeholder-delimited export into `## Page N` sections."""
    pages = body.split(PAGE_BREAK)
    parts = [MARKER, "", f"# {stem}", ""]
    empty = 0
    for i, page in enumerate(pages, 1):
        text = page.strip()
        if len(text) < 20:
            empty += 1
            parts.append(f"## Page {i}\n\n[no extractable text -- likely image/scan]\n")
        else:
            parts.append(f"## Page {i}\n\n{text}\n")
    return "\n".join(parts).rstrip() + "\n", len(pages), empty


def check_docling_api():
    """Fail loudly on a docling too old for the two options this script depends on.

    Both failures would be SILENT otherwise: no page markers (breaks every
    page-anchored quote downstream) or padded tables (doubles corpus token cost).
    """
    import inspect
    from docling_core.types.doc.document import DoclingDocument

    params = inspect.signature(DoclingDocument.export_to_markdown).parameters
    missing = [p for p in ("page_break_placeholder", "compact_tables") if p not in params]
    if missing:
        log(f"docling is too old -- export_to_markdown lacks {', '.join(missing)}.")
        log("Upgrade: pip install -U docling  (see scripts/requirements.txt)")
        sys.exit(2)


def convert_one(conv, pdf_path):
    stem = os.path.splitext(os.path.basename(pdf_path))[0]
    result = conv.convert(pdf_path)
    doc = result.document
    # compact_tables strips docling's cell padding: same pipes, same content, ~half
    # the characters -- the corpus is read by agents, so padding is pure token cost
    body = doc.export_to_markdown(page_break_placeholder=PAGE_BREAK, compact_tables=True)
    md, pages, empty = paginate(body, stem)
    tables = len(getattr(doc, "tables", []) or [])
    return md, pages, empty, tables


def audit(md_text):
    """Integrity signals downstream actually depends on."""
    return {
        "chars": len(md_text),
        "pipes": md_text.count("|"),
        "pages": len(re.findall(r"^## Page \d+$", md_text, re.M)),
    }


def is_mark_scheme(path, pattern):
    return bool(re.search(pattern, os.path.basename(path), re.I))


def gate(records, ms_pattern):
    """Table-integrity gate. Returns (ok, failures, warnings)."""
    failures = [r for r in records if r["is_mark_scheme"] and r["pipes"] == 0 and r["chars"] > NO_TEXT_CHARS]
    warnings = [r for r in records if not r["is_mark_scheme"] and r["pipes"] == 0 and r["tables"] not in (0, None)]
    return (not failures), failures, warnings


def report(records, ms_pattern, root, no_text, scope=None):
    """scope=None means the whole corpus; anything else is a partial run whose
    verdict must not be filed as the corpus-wide one."""
    ok, failures, warnings = gate(records, ms_pattern)
    ms = [r for r in records if r["is_mark_scheme"]]
    log("")
    if scope:
        log(f"PARTIAL RUN ({scope}) -- this verdict covers only what was converted here.")
        log("The corpus-wide gate is not satisfied until a full run or --verify passes.")
    log(f"TABLE INTEGRITY: {len(ms)} mark scheme(s) checked, {len(failures)} with zero table pipes")
    if not ms:
        # A gate that checks nothing passes vacuously -- the exact silent-success
        # shape F17 is about. Refuse to certify a corpus with no mark schemes in it.
        ok = False
        log("")
        log("=" * 72)
        log("CONVERSION GATE FAILED -- NO MARK SCHEMES RECOGNISED")
        log("=" * 72)
        log(f"Nothing under this root matched the mark-scheme pattern: {ms_pattern}")
        log("Either the corpus has no mark schemes (it must, before /hero-1-research)")
        log("or this board names them differently -- pass --ms-pattern to match them.")
        log("The gate is not allowed to pass by checking zero files.")
    if no_text:
        log("")
        log(f"{len(no_text)} doc(s) had ~no extractable text (need OCR/PDF-direct "
            f"fallback -- record in corpus.known_casualties):")
        for r in no_text:
            log("   " + r["file"])
    if warnings:
        log("")
        log(f"NOTE: {len(warnings)} non-mark-scheme doc(s) lost tables docling detected "
            f"-- spot-check if they carry data tables:")
        for r in warnings[:10]:
            log(f"   {r['file']}  ({r['tables']} tables detected, 0 pipes in output)")
    if failures:
        log("")
        log("=" * 72)
        log("CONVERSION GATE FAILED -- DO NOT SET corpus.conversion.status = complete")
        log("=" * 72)
        log("A mark scheme with zero pipe characters has no table structure left.")
        log("Every marking point R2 quotes from these files is unreliable:")
        for r in failures:
            log(f"   {r['file']}  ({r['chars']} chars, {r['pages']}p, 0 pipes)")
        log("")
        log("Fix before proceeding: confirm the PDF has a text layer (a scan needs")
        log("do_ocr=True), then re-run. If a file genuinely has no tables, record it")
        log("in project.json -> corpus.known_casualties and re-run --verify.")
    elif ok:
        log("")
        log("CONVERSION GATE PASSED -- every mark scheme retained table structure.")

    name = "conversion-report.json"
    if scope:
        # never overwrite the corpus-wide verdict with a shard's
        name = "conversion-report--" + re.sub(r"[^A-Za-z0-9._-]+", "-", scope).strip("-") + ".json"
    out = os.path.join(root, name)
    try:
        with open(out, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "engine": MARKER,
                    "ms_pattern": ms_pattern,
                    "scope": scope or "full corpus",
                    "gate_passed": ok,
                    "gate_covers_whole_corpus": scope is None,
                    "files": records,
                    "failures": [r["file"] for r in failures],
                    "no_text": [r["file"] for r in no_text],
                },
                f,
                indent=2,
            )
        log(f"\nReport: {out}")
    except Exception as e:
        log(f"\n(could not write conversion-report.json: {e})")
    return ok


def find_pdfs(search_root):
    pdfs = []
    for dirpath, _, files in os.walk(search_root):
        for fn in files:
            if fn.lower().endswith(".pdf"):
                pdfs.append(os.path.join(dirpath, fn))
    return sorted(pdfs)


def find_mds(search_root):
    mds = []
    for dirpath, _, files in os.walk(search_root):
        for fn in files:
            if fn.lower().endswith(".md"):
                mds.append(os.path.join(dirpath, fn))
    return sorted(mds)


def main():
    ap = argparse.ArgumentParser(description="Convert a Project Hero PDF corpus to markdown (docling).")
    ap.add_argument("root", help="corpus root (an existing directory)")
    ap.add_argument("--subdir", help="restrict to one subfolder of ROOT")
    ap.add_argument("--limit", type=int, default=0, help="convert only the first N (smoke test)")
    ap.add_argument("--verify", action="store_true", help="audit existing .md only; convert nothing")
    ap.add_argument("--ms-pattern", default=DEFAULT_MS_PATTERN, help="regex identifying mark-scheme filenames")
    args = ap.parse_args()

    root = args.root
    if not os.path.isdir(root):
        log(f"ROOT is not a directory: {root}")
        sys.exit(2)
    search_root = os.path.join(root, args.subdir) if args.subdir else root

    scope_bits = []
    if args.subdir:
        scope_bits.append(f"subdir={args.subdir}")
    if args.limit:
        scope_bits.append(f"limit={args.limit}")
    scope = ", ".join(scope_bits) or None

    records = []
    no_text = []

    if args.verify:
        mds = find_mds(search_root)
        log(f"VERIFY: auditing {len(mds)} existing .md file(s) under {search_root}\n")
        for p in mds:
            try:
                text = open(p, encoding="utf-8", errors="replace").read()
            except Exception as e:
                log(f"UNREADABLE {p}: {e}")
                continue
            a = audit(text)
            rec = {
                "file": os.path.relpath(p, root),
                "engine": text.split("\n", 1)[0].strip() if text.startswith("<!--") else "unknown",
                "is_mark_scheme": is_mark_scheme(p, args.ms_pattern),
                "tables": None,
                **a,
            }
            records.append(rec)
            if a["chars"] < NO_TEXT_CHARS:
                no_text.append(rec)
        sys.exit(0 if report(records, args.ms_pattern, root, no_text, scope) else 1)

    pdfs = find_pdfs(search_root)
    if args.limit:
        pdfs = pdfs[: args.limit]
    if not pdfs:
        log(f"No PDFs found under {search_root}")
        sys.exit(2)

    check_docling_api()
    log("Loading docling models (first run downloads layout + table models)...")
    t0 = time.time()
    conv = build_converter()
    log(f"Models ready in {time.time() - t0:.1f}s\n")

    conv_n = skip = failed = 0
    run_start = time.time()
    for i, pdf in enumerate(pdfs, 1):
        rel = os.path.relpath(pdf, root)
        md_path = os.path.splitext(pdf)[0] + ".md"
        if already_done(md_path):
            skip += 1
            # still audit it, so the gate covers the whole corpus on a resumed run
            text = open(md_path, encoding="utf-8", errors="replace").read()
            records.append({
                "file": os.path.relpath(md_path, root),
                "engine": MARKER,
                "is_mark_scheme": is_mark_scheme(md_path, args.ms_pattern),
                "tables": None,
                **audit(text),
            })
            continue
        try:
            t = time.time()
            md, pages, empty, tables = convert_one(conv, pdf)
            with open(md_path, "w", encoding="utf-8", newline="\n") as f:
                f.write(md)
            conv_n += 1
            a = audit(md)
            rec = {
                "file": os.path.relpath(md_path, root),
                "engine": MARKER,
                "is_mark_scheme": is_mark_scheme(md_path, args.ms_pattern),
                "tables": tables,
                **a,
            }
            records.append(rec)
            flags = ""
            if a["chars"] < NO_TEXT_CHARS:
                no_text.append(rec)
                flags += "  <-- NO TEXT (scan?)"
            if rec["is_mark_scheme"] and a["pipes"] == 0 and a["chars"] > NO_TEXT_CHARS:
                flags += "  <-- NO TABLES (gate will fail)"
            log(f"[{i}/{len(pdfs)}] {rel}  ({a['chars']} chars, {pages}p, {empty} empty, "
                f"{a['pipes']} pipes, {tables} tables, {time.time() - t:.1f}s){flags}")
        except Exception as e:
            failed += 1
            log(f"[{i}/{len(pdfs)}] FAILED  {rel}  -> {e}")
            log(traceback.format_exc())

    log(f"\nDONE converted={conv_n} skipped={skip} failed={failed} total={len(pdfs)} "
        f"in {(time.time() - run_start) / 60:.1f} min")
    ok = report(records, args.ms_pattern, root, no_text, scope)
    sys.exit(0 if (ok and failed == 0) else 1)


if __name__ == "__main__":
    main()
