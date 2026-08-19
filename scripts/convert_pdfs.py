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

THREE FURTHER GATES/CHECKS (F32, F44/F58, F62 -- 1PH0, August 2026), because the
table gate is aimed at ONE failure mode and was blind to the rest:

* LEGIBILITY GATE (F32): a non-standard font encoding can make an engine emit
  glyph indices ("## /0 /1 /2 /3 ...") instead of characters. The output passes
  the table gate, looks complete, and is unreadable -- two 1PH0 examiner reports
  were 80% and 76% glyph-index lines and downstream briefs counted them as
  usable. Any file that is mostly glyph-index lines, or that contains zero lines
  of subject-neutral corpus vocabulary (candidates/marks/question/answer), FAILS.
  Record failures in project.json -> corpus.known_casualties WITH the reason --
  a silently unusable file is worse than a missing one, because thin results
  from it look like genuine thinness.

* SPEC ENGINE + BOLD GATE (F44/F58/F64): docling drops BOLD -- and Edexcel marks
  Higher-tier-only spec content in bold, so a docling-converted specification is
  tier-blind AND (F58) can silently lose statement content ("g energy" vanished
  from 2.4; three whole sub-items across one spec). pymupdf4llm preserves both,
  so files matching --spec-pattern are converted with pymupdf4llm instead. The
  BOLD GATE then fails any spec whose source PDF carries bold spans while the
  converted markdown carries no `**`. Per F64, engine choice is PER DOCUMENT
  TYPE, not per corpus: the docling-vs-pymupdf4llm result INVERTS between mark
  schemes and question papers (docling loses QP figure text; pymupdf4llm loses
  MS guidance words), so never swap the engine wholesale in either direction.

* ORPHAN-PART CHECK (F62, report-only): question part labels in an exam paper
  are strictly sequential -- a "(ii)" whose predecessor is not "(i)" means the
  conversion dropped content (1PH0: a whole stem + figure + part (i) vanished,
  leaving an orphaned satellite question that five stages then reasoned about).
  Discontinuities are reported per question-paper file for human follow-up.

* SUPERSCRIPT AUDIT (report-only, 2026-08-10): docling flattens superscripted
  digits into the adjacent number -- "65²" converts to "652", easy to misread
  as a different value (recurring across multiple 4PH1 sittings). The source
  PDF is scanned for superscripted spans (PyMuPDF span flags); files that
  carry them are listed so numeric values get verified against the PDF, and
  recurring cases recorded in corpus.content_limitations.

* PER-PAGE SCAN CHECK (report-only, 2026-08-10): the whole-file no-text
  threshold misses a long clean PDF with a few scanned pages inside it. Any
  file above the threshold that still contains [no extractable text] page
  placeholders is listed for OCR/PDF-direct follow-up of those pages.

MS partial-row-loss cross-check lives in scripts/ms_row_coverage.py (run it
after conversion): the pipe-count gate passes a mark scheme that lost single
rows/cells while the table still parses -- 10+ verified instances in one 4PH1
wave -- so per-question MS coverage is reconciled against the QP's
"Total for Question N" lines there.

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
SPEC_MARKER = "<!-- pymupdf4llm-extract v1 -->"
KNOWN_MARKERS = (MARKER, SPEC_MARKER)
PAGE_BREAK = "<!--__HERO_PAGE_BREAK__-->"

# Filenames matching this are mark schemes, and are held to the table-integrity
# gate. Covers the human-readable form and the board abbreviations seen so far
# (Edexcel ms/msc/rms, CIE _ms_). Override with --ms-pattern for anything else --
# check the hit list the run prints before trusting the gate on a new board.
DEFAULT_MS_PATTERN = r"mark[\s_-]*scheme|\b(r?ms|msc)\b|[\s_-](r?ms|msc)[\s_.-]"

# Filenames matching this are specifications: converted with pymupdf4llm (bold
# survives -- boards use bold semantically, e.g. Edexcel GCSE Higher-tier
# marking) and held to the bold gate (F44/F58).
DEFAULT_SPEC_PATTERN = r"specification|syllabus"

# Filenames matching this are question papers: held to the orphan-part check
# (F62, report-only).
DEFAULT_QP_PATTERN = r"question[\s_-]*paper|\bqp\b|[\s_-]qp[\s_.-]"

NO_TEXT_CHARS = 200  # below this a doc is treated as a scan

# F32 legibility gate. Glyph-index lines look like "## /0 /1 /2 /3/4 /5 ..." --
# an engine emitting font glyph ids instead of characters. Real 1PH0 failures
# were 80% and 76% such lines against a clean-file baseline of 0%, so the
# threshold needs no tuning.
GLYPH_INDEX_LINE = re.compile(r"^[#|\s]*(/[0-9A-Fa-f]+\s*)+\|?\s*$")
GLYPH_SHARE_FAIL = 0.30
# Subject-neutral corpus vocabulary: any legible exam document (QP/MS/ER/spec)
# contains at least one of these somewhere.
VOCAB_RE = re.compile(r"candidates?|marks?|questions?|answers?", re.I)


def log(msg):
    print(msg, flush=True)


def _fail_docling_import(exc):
    """Diagnose a docling import failure LOUDLY and correctly (CIE 5070 onboarding,
    19 Aug 2026): a broken environment raised ModuleNotFoundError on
    docling.document_converter and was misread as "the script uses the v1.x API" --
    with a proposed fix of downgrading and RE-PINNING docling, which would have
    forked the corpus (see requirements.txt: the pin is determinism-critical).

    The imports below ARE the docling v2 API and import cleanly against the pinned
    docling==2.107.0. If they fail, the problem is ALWAYS this interpreter's
    environment, never the script: wrong interpreter/venv for the install, a
    partial install, or a shadowing `docling` directory on sys.path (namespace
    package -- docling imports but __file__ is None and submodules are missing)."""
    log("=" * 72)
    log("DOCLING IMPORT FAILED -- this is an ENVIRONMENT fault, not a script fault")
    log(f"  error: {exc}")
    log(f"  interpreter: {sys.executable}")
    try:
        import docling
        loc = getattr(docling, "__file__", None)
        log(f"  'import docling' resolves to: {loc}")
        if loc is None:
            log("  __file__ is None -> NAMESPACE PACKAGE: a shadowing or half-"
                "installed 'docling' directory, not a real install")
    except ImportError:
        log("  'import docling' fails outright -> docling is not installed in"
            " THIS interpreter's environment")
    log("Fix, using the SAME interpreter shown above:")
    log(f"  {sys.executable} -m pip install --force-reinstall -r scripts/requirements.txt")
    log("Do NOT downgrade docling or change the pin: this import path IS the v2")
    log("API, and a different docling version silently forks a committed corpus.")
    log("=" * 72)
    sys.exit(1)


def build_converter():
    try:
        from docling.document_converter import DocumentConverter, PdfFormatOption
        from docling.datamodel.base_models import InputFormat
        from docling.datamodel.pipeline_options import PdfPipelineOptions
        from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
    except ImportError as exc:
        _fail_docling_import(exc)

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


def already_done(md_path, expected_marker):
    """Resumable only against the engine this file type is SUPPOSED to use --
    a spec previously converted by docling must be reconverted (F44/F58), so
    it does not count as done."""
    if not os.path.exists(md_path) or os.path.getsize(md_path) == 0:
        return False
    try:
        with open(md_path, "r", encoding="utf-8") as f:
            return f.readline().strip() == expected_marker
    except Exception:
        return False


def convert_one_spec(pdf_path):
    """Specification conversion via pymupdf4llm (F44/F58): preserves bold --
    which boards use semantically -- and kept full statement bodies that
    docling dropped from spec tables in production."""
    import pymupdf4llm

    stem = os.path.splitext(os.path.basename(pdf_path))[0]
    chunks = pymupdf4llm.to_markdown(pdf_path, page_chunks=True)
    parts = [SPEC_MARKER, "", f"# {stem}", ""]
    empty = 0
    for i, chunk in enumerate(chunks, 1):
        text = (chunk.get("text") or "").strip()
        if len(text) < 20:
            empty += 1
            parts.append(f"## Page {i}\n\n[no extractable text -- likely image/scan]\n")
        else:
            parts.append(f"## Page {i}\n\n{text}\n")
    md = "\n".join(parts).rstrip() + "\n"
    return md, len(chunks), empty, None


def lower_priority():
    """--nice: a full-corpus conversion monopolises the machine (2026-08-10
    feedback). Drop the process below normal priority so the desktop stays
    usable; the run just takes a little longer."""
    try:
        if os.name == "nt":
            import ctypes
            handle = ctypes.windll.kernel32.GetCurrentProcess()
            ctypes.windll.kernel32.SetPriorityClass(handle, 0x00004000)  # BELOW_NORMAL_PRIORITY_CLASS
        else:
            os.nice(10)
        log("(running at below-normal priority: --nice)")
    except Exception as e:
        log(f"(--nice requested but could not lower priority: {e})")


def limit_cpus(n):
    """--cpu-limit: pin the process to the first N logical CPUs.

    Measured 2026-08-11, i5-1235U (2 P-cores + 8 E-cores = 12 logical), on a
    38-page mark scheme. Output was byte-identical at every setting:

        all 12    103.8 s wall    611 CPU-s
        first 8    96.7 s         583 CPU-s
        first 6   109.2 s         521 CPU-s
        first 4    98.0 s         383 CPU-s   <- best: -37% CPU, no wall cost
        first 2   175.8 s         335 CPU-s   (wall +69%, not worth it)

    Docling oversubscribes a hybrid CPU: threads land on the slow E-cores and
    burn CPU spin-waiting. Pinning to the P-cores removes that waste. --nice
    does NOT achieve this on its own -- the 8-CPU row above is essentially
    --nice alone, and 5% is inside run-to-run noise.

    Docling/torch's own knobs were all verified ineffective here:
    AcceleratorOptions(num_threads=4), OMP_NUM_THREADS=4 and
    torch.set_num_interop_threads(4) each left parallelism at ~6.1x. Only OS
    affinity binds.

    Pick N = the machine's performance-core count (typically half the logical
    CPU count on a hybrid Intel part; on a uniform CPU, roughly half the cores).
    """
    total = os.cpu_count() or 1
    if n < 1 or n > total:
        log(f"(--cpu-limit {n} out of range 1..{total}; ignored)")
        return
    try:
        if os.name == "nt":
            import ctypes
            k = ctypes.windll.kernel32
            k.SetProcessAffinityMask.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
            if not k.SetProcessAffinityMask(k.GetCurrentProcess(), (1 << n) - 1):
                raise OSError(ctypes.get_last_error())
        else:
            os.sched_setaffinity(0, set(range(n)))
        log(f"(pinned to {n} of {total} logical CPUs: --cpu-limit)")
    except Exception as e:
        log(f"(--cpu-limit requested but could not set affinity: {e})")


def pdf_superscript_count(pdf_path):
    """Count superscripted spans in the source PDF (PyMuPDF flag bit 0).
    Returns None when the check cannot run (no fitz, unreadable PDF)."""
    try:
        import fitz
    except ImportError:
        return None
    try:
        n = 0
        doc = fitz.open(pdf_path)
        for page in doc:
            for block in page.get_text("dict").get("blocks", []):
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        if span.get("flags", 0) & 1:
                            n += 1
        return n
    except Exception:
        return None


def pdf_has_bold(pdf_path):
    """True if the source PDF carries any bold text span (fitz/PyMuPDF).
    Returns None when the check itself cannot run -- callers must treat None
    as 'gate could not run', never as False."""
    try:
        import fitz
    except ImportError:
        return None
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            for block in page.get_text("dict").get("blocks", []):
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        if span.get("flags", 0) & 16 or "bold" in span.get("font", "").lower():
                            return True
        return False
    except Exception:
        return None


PART_LABEL = re.compile(r"^\s*[*\-]?\s*\*?\((i{1,3}|iv|[a-h])\)", re.M)
ROMAN_ORDER = {"i": 1, "ii": 2, "iii": 3, "iv": 4}


def part_discontinuities(md_text):
    """F62 orphan-part check (report-only): part labels are strictly sequential
    in an exam paper. Valid transitions are X -> successor(X) and X -> (i)/(a)
    (a new question's first part). Anything else means the conversion dropped
    the intervening content. Roman and alphabetic sequences tracked separately."""
    issues = 0
    prev = {"roman": None, "alpha": None}
    for m in PART_LABEL.finditer(md_text):
        label = m.group(1)
        if label in ROMAN_ORDER:
            kind, val = "roman", ROMAN_ORDER[label]
        else:
            kind, val = "alpha", ord(label) - ord("a") + 1
        last = prev[kind]
        if val != 1 and (last is None or val != last + 1):
            issues += 1
        prev[kind] = val
    return issues


TOTAL_MARKER = re.compile(r"\(?\s*Total\s+for\s+Question\s+(\d+)\s*[=:]\s*(\d+)\s*marks?", re.I)
MARK_TAG = re.compile(r"\(\s*(\d{1,2})\s*\)")
TALLY_ONLY_CELL = re.compile(r"^\s*(?:\(\s*\d{1,2}\s*\)[\s.]*){2,}$")


def qp_total_audit(md_text):
    """F165 structural gate (report-only): the conversion can drop whole question
    parts -- or whole questions -- leaving NO gap marker, and the surrounding
    markdown reads as continuous (1PH0: Q10 vanished entirely, 11 marks; two
    silent drops in one file; four instances across two waves, every one found
    by an agent at the PDF, never by a gate). The printed total markers are the
    paper's own structural self-description, so audit against them:
    - a missing question NUMBER in the marker sequence = a dropped question (or
      a dropped marker, which flags the same passage);
    - a question whose per-part mark tags sum BELOW its printed total = dropped
      parts inside it. One-sided by design: stray parenthesised numbers can
      only raise the sum, so only a shortfall is evidence (a sweep for the
      wrong thing present is not a sweep for the right thing absent).
    Returns None where a QP prints no such markers (not every board does)."""
    totals = [(int(m.group(1)), int(m.group(2)), m.start(), m.end())
              for m in TOTAL_MARKER.finditer(md_text)]
    if not totals:
        return None
    nums = [n for n, _, _, _ in totals]
    missing = sorted(set(range(1, max(nums) + 1)) - set(nums))
    undersum = []
    prev_end = 0
    for n, total, start, end in totals:
        span = md_text[prev_end:start]
        tag_sum = sum(int(t) for t in MARK_TAG.findall(span) if 1 <= int(t) <= 20)
        if tag_sum < total:
            undersum.append({"question": n, "printed_total": total, "tag_sum": tag_sum})
        prev_end = end
    return {"markers": len(totals),
            "missing_question_numbers": missing,
            "undersummed_questions": undersum}


def ms_tally_only_cells(md_text):
    """F165 variant (report-only): conversion can destroy a mark scheme's ANSWER
    content while leaving its structure intact -- 1H 2023 June Q7(a)(iii)'s
    entire marking cell reduced to bare '(1) (1) (1)', every nuclide symbol
    gone, mark tallies surviving so the row reads as complete. A table cell
    containing ONLY mark tags is almost never legitimate; count them."""
    count = 0
    for line in md_text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("|") and line.count("|") >= 3:
            if any(TALLY_ONLY_CELL.match(c) for c in line.split("|")[1:-1]):
                count += 1
    return count


def pdf_duplicate_groups(search_root):
    """F167 (report-only): MD5 every source PDF and report byte-identical
    groups. Duplication is LEGITIMATE for one class only -- a board's
    'insufficient entries' null examiner report, issued once per tier-cohort
    per sitting and filed into every affected paper's folder (it carries no
    internal identifier, so nothing downstream can tell the copies apart).
    Two non-null files sharing a hash is an acquisition defect the pipeline
    otherwise has no way to see. The sweep converts an anomaly into a fact."""
    import hashlib
    by_hash = {}
    for pdf in find_pdfs(search_root):
        h = hashlib.md5()
        try:
            with open(pdf, "rb") as f:
                for chunk in iter(lambda: f.read(1 << 20), b""):
                    h.update(chunk)
        except OSError:
            continue
        by_hash.setdefault((h.hexdigest(), os.path.getsize(pdf)), []).append(pdf)
    return [{"md5": k[0], "bytes": k[1],
             "files": [os.path.relpath(p, search_root) for p in v]}
            for k, v in sorted(by_hash.items()) if len(v) > 1]


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
    """Integrity signals downstream actually depends on.

    The Unicode counts are the F20 artifact sweep: these classes survive a
    passing table gate, and PUA (symbol-font) characters return ZERO to a
    plain grep -- a mechanical count here is the only reliable detector.
    The 1PH0 corpus carried 910 PUA glyphs including a Symbol-font tick that
    was (redundantly, by luck) the marker of a correct MCQ option."""
    pua = ligatures = math_alnum = replacement = 0
    for ch in md_text:
        cp = ord(ch)
        if 0xE000 <= cp <= 0xF8FF:
            pua += 1
        elif 0xFB00 <= cp <= 0xFB06:
            ligatures += 1
        elif 0x1D400 <= cp <= 0x1D7FF:
            math_alnum += 1
        elif cp == 0xFFFD:
            replacement += 1
    # F32 legibility signals
    nonblank = [ln for ln in md_text.splitlines() if ln.strip()]
    glyph_lines = sum(1 for ln in nonblank if GLYPH_INDEX_LINE.match(ln))
    vocab_lines = sum(1 for ln in nonblank if VOCAB_RE.search(ln))
    return {
        "chars": len(md_text),
        "pipes": md_text.count("|"),
        "pages": len(re.findall(r"^## Page \d+$", md_text, re.M)),
        "pua_chars": pua,
        "ligature_glyphs": ligatures,
        "math_alnum_glyphs": math_alnum,
        "replacement_chars": replacement,
        "nonblank_lines": len(nonblank),
        "glyph_index_lines": glyph_lines,
        "glyph_index_share": round(glyph_lines / len(nonblank), 3) if nonblank else 0.0,
        "vocab_lines": vocab_lines,
        "bold_marks": md_text.count("**") // 2,
        # per-page scan check: placeholder pages inside an otherwise-clean file
        "empty_pages": md_text.count("[no extractable text -- likely image/scan]"),
    }


def is_mark_scheme(path, pattern):
    return bool(re.search(pattern, os.path.basename(path), re.I))


def is_spec(path, pattern):
    return bool(re.search(pattern, os.path.basename(path), re.I))


def is_question_paper(path, pattern):
    return bool(re.search(pattern, os.path.basename(path), re.I))


def gate(records, ms_pattern):
    """Table-integrity + legibility + bold gates.
    Returns (ok, table_failures, warnings, legibility_failures, bold_failures).
    NOTE: report() additionally fails the run when the gate would have checked
    ZERO mark schemes or ZERO specifications -- a gate that processed nothing
    has failed, not passed (F63/F69)."""
    failures = [r for r in records if r["is_mark_scheme"] and r["pipes"] == 0 and r["chars"] > NO_TEXT_CHARS]
    warnings = [r for r in records if not r["is_mark_scheme"] and r["pipes"] == 0 and r["tables"] not in (0, None)]
    # F32: mostly glyph-index lines, or zero corpus vocabulary in a real file
    legibility = [
        r for r in records
        if r["chars"] > NO_TEXT_CHARS
        and (r.get("glyph_index_share", 0) >= GLYPH_SHARE_FAIL or r.get("vocab_lines", 1) == 0)
    ]
    # F44: spec whose PDF has bold spans while the markdown has none -- and
    # the case where the bold check itself could not run is ALSO a failure
    # (bold_in_pdf None), never a silent pass
    bold = [
        r for r in records
        if r.get("is_spec")
        and r.get("bold_in_pdf") is not False
        and (r.get("bold_in_pdf") is None or r.get("bold_marks", 0) == 0)
    ]
    ok = not failures and not legibility and not bold
    return ok, failures, warnings, legibility, bold


def report(records, ms_pattern, root, no_text, scope=None, no_spec_expected=False):
    """scope=None means the whole corpus; anything else is a partial run whose
    verdict must not be filed as the corpus-wide one."""
    ok, failures, warnings, legibility, bold = gate(records, ms_pattern)
    ms = [r for r in records if r["is_mark_scheme"]]
    specs = [r for r in records if r.get("is_spec")]
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
    log(f"SPEC BOLD: {len(specs)} specification(s) checked, {len(bold)} failed")
    if not specs and not no_spec_expected:
        # Same F63/F69 shape as the mark-scheme case: the bold gate checked
        # nothing, so it must not pass (2026-08-10 feedback -- it did, vacuously).
        ok = False
        log("")
        log("=" * 72)
        log("CONVERSION GATE FAILED -- NO SPECIFICATION RECOGNISED")
        log("=" * 72)
        log("Nothing under this root matched the spec pattern, so the bold gate")
        log("(F44/F58 tier-marking survival) checked zero files. Either the spec is")
        log("named differently (pass --spec-pattern), or it is genuinely stored")
        log("outside this root -- in that case pass --no-spec to assert that")
        log("deliberately and run this script over the spec's own directory too.")
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
    # F20 Unicode artifact sweep -- report-only, not a gate. PUA glyphs are the
    # dangerous class: invisible to a plain grep, and occasionally the sole
    # carrier of meaning (a Symbol-font tick marking a correct MCQ option).
    unicode_hits = [r for r in records
                    if r.get("pua_chars") or r.get("ligature_glyphs") or r.get("replacement_chars")]
    if unicode_hits:
        log("")
        log(f"UNICODE AUDIT (F20): {len(unicode_hits)} file(s) carry PUA/ligature/replacement "
            f"characters -- these survive the table gate and PUA glyphs return zero to a plain grep.")
        log("Open the highest-count files and check no glyph is the SOLE carrier of meaning")
        log("(e.g. a tick marking a correct MCQ option); recover such items from the PDF and")
        log("record them in corpus.known_casualties. Top offenders:")
        for r in sorted(unicode_hits, key=lambda x: -(x.get("pua_chars", 0) or 0))[:10]:
            log(f"   {r['file']}  (PUA {r.get('pua_chars', 0)}, ligatures {r.get('ligature_glyphs', 0)}, "
                f"replacement {r.get('replacement_chars', 0)})")
    if legibility:
        log("")
        log("=" * 72)
        log("LEGIBILITY GATE FAILED (F32) -- these files converted but are UNREADABLE")
        log("=" * 72)
        log("Mostly glyph-index lines (non-standard font encoding) or zero corpus")
        log("vocabulary. A silently unusable file is worse than a missing one: thin")
        log("results from it look like genuine thinness. Record EACH in project.json ->")
        log("corpus.known_casualties with the reason, or re-convert from a better source:")
        for r in legibility:
            log(f"   {r['file']}  (glyph-index share {r.get('glyph_index_share', 0):.0%}, "
                f"vocab lines {r.get('vocab_lines', 0)})")
    if bold:
        log("")
        log("=" * 72)
        log("BOLD GATE FAILED (F44) -- specification lost its bold, or check could not run")
        log("=" * 72)
        log("Boards use bold semantically (Edexcel GCSE: bold = Higher tier only). A spec")
        log("with no ** in its markdown while the PDF carries bold spans is tier-blind,")
        log("and every downstream tier claim inherits that silently:")
        for r in bold:
            why = ("bold check could not run (pip install pymupdf)"
                   if r.get("bold_in_pdf") is None
                   else f"PDF has bold, markdown has {r.get('bold_marks', 0)} ** pairs")
            log(f"   {r['file']}  ({why})")
    # Per-page scan check (2026-08-10): a long clean PDF with a few scanned
    # pages passes the whole-file threshold; these need OCR/PDF-direct
    # follow-up of just those pages.
    partial_scans = [r for r in records if r["chars"] > NO_TEXT_CHARS and r.get("empty_pages", 0) > 0]
    if partial_scans:
        log("")
        log(f"PER-PAGE SCAN CHECK (report-only): {len(partial_scans)} text-bearing file(s) contain "
            f"no-text page placeholders -- scanned/image pages inside an otherwise clean file.")
        log("Check each flagged page against the PDF; recover what matters (OCR or PDF-direct)")
        log("and record unrecovered pages in corpus.known_casualties:")
        for r in sorted(partial_scans, key=lambda x: -x.get("empty_pages", 0))[:10]:
            log(f"   {r['file']}  ({r['empty_pages']} empty page(s) of {r['pages']})")
    # Superscript audit (2026-08-10): docling flattens "65²" to "652".
    supers = [r for r in records if r.get("superscript_spans")]
    if supers:
        log("")
        log(f"SUPERSCRIPT AUDIT (report-only): {len(supers)} file(s) carry superscripted spans in "
            f"the source PDF. docling flattens these into the adjacent digits ('65²' -> '652'),")
        log("which reads as a different number. Verify numeric values in these files against the")
        log("PDF before quoting; record recurring cases in corpus.content_limitations:")
        for r in sorted(supers, key=lambda x: -(x.get("superscript_spans") or 0))[:10]:
            log(f"   {r['file']}  ({r['superscript_spans']} superscripted span(s))")
    orphaned = [r for r in records if r.get("part_discontinuities")]
    if orphaned:
        log("")
        log(f"ORPHAN-PART CHECK (F62, report-only): {len(orphaned)} question paper(s) have "
            f"non-sequential part labels -- a (ii) with no (i) before it means the")
        log("conversion dropped the intervening content (a stem, a figure, a whole part).")
        log("Read each in place against the PDF before any stage asserts an absence:")
        for r in sorted(orphaned, key=lambda x: -x["part_discontinuities"])[:10]:
            log(f"   {r['file']}  ({r['part_discontinuities']} discontinuity(ies))")
    # F165: totals audit -- silent whole-question / whole-part drops.
    qp_bad = [r for r in records if r.get("qp_total_audit")
              and (r["qp_total_audit"]["missing_question_numbers"]
                   or r["qp_total_audit"]["undersummed_questions"])]
    if qp_bad:
        log("")
        log(f"QUESTION-TOTALS AUDIT (F165, report-only): {len(qp_bad)} question paper(s) fail "
            "reconciliation against their own printed '(Total for Question N = M marks)' markers.")
        log("A missing question number means a whole question (or its marker) was dropped; a")
        log("mark-tag sum below the printed total means parts were dropped inside it. Recover")
        log("each from the PDF or the second-engine tree before any absence claim is written:")
        for r in qp_bad[:10]:
            au = r["qp_total_audit"]
            bits = []
            if au["missing_question_numbers"]:
                bits.append(f"missing Q{', Q'.join(map(str, au['missing_question_numbers']))}")
            for u in au["undersummed_questions"]:
                bits.append(f"Q{u['question']} tags sum {u['tag_sum']} < printed {u['printed_total']}")
            log(f"   {r['file']}  ({'; '.join(bits)})")
    ms_tally = [r for r in records if r.get("ms_tally_only_cells")]
    if ms_tally:
        log("")
        log(f"MS TALLY-ONLY-CELL CHECK (F165 variant, report-only): {len(ms_tally)} mark scheme(s) "
            "carry table cells containing ONLY mark tags ('(1) (1) (1)') -- answer content")
        log("destroyed with structure intact (1H 2023 June Q7(a)(iii): every nuclide symbol gone,")
        log("tallies surviving). Recover each cell from the PDF; where the RENDER is also corrupt,")
        log("triangulate from a second document (W-176):")
        for r in sorted(ms_tally, key=lambda x: -x["ms_tally_only_cells"])[:10]:
            log(f"   {r['file']}  ({r['ms_tally_only_cells']} tally-only cell(s))")
    dup_groups = pdf_duplicate_groups(root)
    if dup_groups:
        log("")
        log(f"PDF DUPLICATE SWEEP (F167, report-only): {len(dup_groups)} byte-identical group(s).")
        log("Legitimate ONLY for null 'insufficient entries' examiner reports (one notice per")
        log("tier-cohort per sitting, filed into every affected folder -- identity for that class")
        log("rests on the path, which downstream identity checks must record as 'not")
        log("content-verifiable -- null-notice class'). Duplicate QPs or MSs = acquisition defect:")
        for g in dup_groups[:10]:
            log(f"   {g['bytes']} bytes: {', '.join(g['files'])}")
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
        log("CONVERSION GATE PASSED -- table structure, legibility and spec bold all held.")

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
                    "legibility_failures": [
                        {"file": r["file"],
                         "glyph_index_share": r.get("glyph_index_share", 0),
                         "vocab_lines": r.get("vocab_lines", 0),
                         "reason": "glyph-index/unreadable (F32) -- record in corpus.known_casualties"}
                        for r in legibility
                    ],
                    "bold_gate_failures": [r["file"] for r in bold],
                    "part_discontinuity_files": [
                        {"file": r["file"], "count": r["part_discontinuities"]}
                        for r in orphaned
                    ],
                    "qp_total_audit_failures": [
                        {"file": r["file"], **r["qp_total_audit"]} for r in qp_bad
                    ],
                    "ms_tally_only_cell_files": [
                        {"file": r["file"], "cells": r["ms_tally_only_cells"]}
                        for r in ms_tally
                    ],
                    "duplicate_pdf_groups": dup_groups,
                    "no_text": [r["file"] for r in no_text],
                    "partial_scan_files": [
                        {"file": r["file"], "empty_pages": r.get("empty_pages", 0), "pages": r["pages"]}
                        for r in partial_scans
                    ],
                    "superscript_files": [
                        {"file": r["file"], "superscript_spans": r.get("superscript_spans")}
                        for r in supers
                    ],
                    "unicode_artifact_files": [r["file"] for r in unicode_hits],
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
    ap.add_argument("--spec-pattern", default=DEFAULT_SPEC_PATTERN,
                    help="regex identifying specification filenames (converted with pymupdf4llm, bold-gated)")
    ap.add_argument("--qp-pattern", default=DEFAULT_QP_PATTERN,
                    help="regex identifying question-paper filenames (orphan-part check)")
    ap.add_argument("--nice", action="store_true",
                    help="run at below-normal process priority so the machine stays usable")
    ap.add_argument("--cpu-limit", type=int, metavar="N",
                    help="pin to the first N logical CPUs (see limit_cpus(): -37%% CPU at "
                         "N=4 on a 12-logical hybrid part, identical output). Use with --nice.")
    ap.add_argument("--no-spec", action="store_true",
                    help="assert the specification deliberately lives outside this root "
                         "(otherwise a run that recognises zero specs FAILS, F63/F69)")
    args = ap.parse_args()

    if args.nice:
        lower_priority()
    if args.cpu_limit:
        limit_cpus(args.cpu_limit)

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
            spec = is_spec(p, args.spec_pattern)
            rec = {
                "file": os.path.relpath(p, root),
                "engine": text.split("\n", 1)[0].strip() if text.startswith("<!--") else "unknown",
                "is_mark_scheme": is_mark_scheme(p, args.ms_pattern),
                "is_spec": spec,
                "tables": None,
                **a,
            }
            sibling_pdf = os.path.splitext(p)[0] + ".pdf"
            if spec:
                rec["bold_in_pdf"] = pdf_has_bold(sibling_pdf) if os.path.exists(sibling_pdf) else None
            if is_question_paper(p, args.qp_pattern):
                rec["part_discontinuities"] = part_discontinuities(text)
                rec["qp_total_audit"] = qp_total_audit(text)
            if rec["is_mark_scheme"]:
                rec["ms_tally_only_cells"] = ms_tally_only_cells(text)
            if os.path.exists(sibling_pdf):
                rec["superscript_spans"] = pdf_superscript_count(sibling_pdf)
            records.append(rec)
            if a["chars"] < NO_TEXT_CHARS:
                no_text.append(rec)
        sys.exit(0 if report(records, args.ms_pattern, root, no_text, scope, args.no_spec) else 1)

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
        spec = is_spec(pdf, args.spec_pattern)
        expected_marker = SPEC_MARKER if spec else MARKER
        if already_done(md_path, expected_marker):
            skip += 1
            # still audit it, so the gate covers the whole corpus on a resumed run
            text = open(md_path, encoding="utf-8", errors="replace").read()
            rec = {
                "file": os.path.relpath(md_path, root),
                "engine": expected_marker,
                "is_mark_scheme": is_mark_scheme(md_path, args.ms_pattern),
                "is_spec": spec,
                "tables": None,
                **audit(text),
            }
            if spec:
                rec["bold_in_pdf"] = pdf_has_bold(pdf)
            if is_question_paper(md_path, args.qp_pattern):
                rec["part_discontinuities"] = part_discontinuities(text)
                rec["qp_total_audit"] = qp_total_audit(text)
            if rec["is_mark_scheme"]:
                rec["ms_tally_only_cells"] = ms_tally_only_cells(text)
            rec["superscript_spans"] = pdf_superscript_count(pdf)
            records.append(rec)
            continue
        try:
            t = time.time()
            if spec:
                md, pages, empty, tables = convert_one_spec(pdf)
            else:
                md, pages, empty, tables = convert_one(conv, pdf)
            with open(md_path, "w", encoding="utf-8", newline="\n") as f:
                f.write(md)
            conv_n += 1
            a = audit(md)
            rec = {
                "file": os.path.relpath(md_path, root),
                "engine": expected_marker,
                "is_mark_scheme": is_mark_scheme(md_path, args.ms_pattern),
                "is_spec": spec,
                "tables": tables,
                **a,
            }
            if spec:
                rec["bold_in_pdf"] = pdf_has_bold(pdf)
            if is_question_paper(md_path, args.qp_pattern):
                rec["part_discontinuities"] = part_discontinuities(md)
                rec["qp_total_audit"] = qp_total_audit(md)
            if rec["is_mark_scheme"]:
                rec["ms_tally_only_cells"] = ms_tally_only_cells(md)
            rec["superscript_spans"] = pdf_superscript_count(pdf)
            records.append(rec)
            flags = ""
            if a["chars"] < NO_TEXT_CHARS:
                no_text.append(rec)
                flags += "  <-- NO TEXT (scan?)"
            if rec["is_mark_scheme"] and a["pipes"] == 0 and a["chars"] > NO_TEXT_CHARS:
                flags += "  <-- NO TABLES (gate will fail)"
            if a.get("glyph_index_share", 0) >= GLYPH_SHARE_FAIL or a.get("vocab_lines", 1) == 0:
                flags += "  <-- UNREADABLE (legibility gate will fail)"
            log(f"[{i}/{len(pdfs)}] {rel}  ({a['chars']} chars, {pages}p, {empty} empty, "
                f"{a['pipes']} pipes, {tables} tables, {time.time() - t:.1f}s){flags}")
        except Exception as e:
            failed += 1
            log(f"[{i}/{len(pdfs)}] FAILED  {rel}  -> {e}")
            log(traceback.format_exc())

    log(f"\nDONE converted={conv_n} skipped={skip} failed={failed} total={len(pdfs)} "
        f"in {(time.time() - run_start) / 60:.1f} min")
    ok = report(records, args.ms_pattern, root, no_text, scope, args.no_spec)
    sys.exit(0 if (ok and failed == 0) else 1)


if __name__ == "__main__":
    main()
