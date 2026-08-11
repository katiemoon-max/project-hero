"""PROTOTYPE (2026-08-11): convert a Project Hero corpus via a remote
docling-serve host instead of the local CPU.

Why this exists: a full-corpus conversion is ~13.5 CPU-hours on a laptop
(measured, 4PH1: 149 PDFs / 3,734 pages). Offloading it to a spare machine
frees the creator's machine entirely.

THE ONE NON-OBVIOUS BIT -- we ask the server for `json`, not `md`.

docling-serve does NOT expose docling's `compact_tables` export option (checked
against its OpenAPI schema, 2026-08-11), and convert_pdfs.py depends on it:
compact_tables strips docling's cell padding, roughly halving table characters.
Asking the server for markdown would therefore fork the corpus. So the server
returns the DoclingDocument as JSON -- all the expensive layout/TableFormer
inference happens remotely -- and this client runs the identical
export_to_markdown() + paginate() locally, which needs no models and is nearly
free. Output is then byte-identical to a local run.

Specifications are NOT handled here: they go through pymupdf4llm locally for
the F44/F58 bold gate. Run convert_pdfs.py for those (it skips what this
already wrote, and vice versa, via the shared marker).

The server MUST pin docling-slim==2.107.0 / docling-core==2.85.0 to match the
laptop, or the same PDF converts differently on the two machines.

Usage:
  set HERO_DOCLING_API_KEY=<key>
  python remote_convert.py <corpus-root> --server http://<host>:5001 [--limit N]

Verify afterwards with the real gate:
  python convert_pdfs.py <corpus-root> --verify
"""
import argparse
import os
import sys
import time

import requests

# Parity is guaranteed by reusing the pipeline's own constants and pagination
# rather than restating them here.
from convert_pdfs import (
    MARKER,
    PAGE_BREAK,
    DEFAULT_SPEC_PATTERN,
    already_done,
    find_pdfs,
    is_spec,
    log,
    paginate,
)

TIMEOUT_S = 1800


def convert_remote(session, server, pdf_path, api_key):
    """POST one PDF, return (markdown_body, n_tables). Raises on failure."""
    from docling_core.types.doc.document import DoclingDocument

    data = [
        ("to_formats", "json"),
        ("do_ocr", "false"),
        ("do_table_structure", "true"),
        ("table_cell_matching", "true"),
        ("do_formula_enrichment", "false"),
        ("pdf_backend", "pypdfium2"),
        ("include_images", "false"),
        ("table_mode", "accurate"),
    ]
    headers = {"X-Api-Key": api_key} if api_key else {}

    with open(pdf_path, "rb") as fh:
        files = {"files": (os.path.basename(pdf_path), fh, "application/pdf")}
        r = session.post(
            f"{server.rstrip('/')}/v1/convert/file",
            files=files, data=data, headers=headers, timeout=TIMEOUT_S,
        )
    if r.status_code == 401:
        raise RuntimeError("401 from server -- API key missing or wrong "
                           "(set HERO_DOCLING_API_KEY, or --api-key)")
    r.raise_for_status()
    payload = r.json()
    if payload.get("status") not in ("success", "partial_success"):
        raise RuntimeError(f"server status={payload.get('status')} "
                           f"errors={payload.get('errors')}")

    doc = DoclingDocument.model_validate(payload["document"]["json_content"])
    body = doc.export_to_markdown(page_break_placeholder=PAGE_BREAK,
                                  compact_tables=True)
    return body, len(getattr(doc, "tables", []) or [])


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("root", help="corpus root (an existing directory)")
    ap.add_argument("--server", required=True, help="e.g. http://192.168.1.42:5001")
    ap.add_argument("--api-key", default=os.environ.get("HERO_DOCLING_API_KEY", ""))
    ap.add_argument("--limit", type=int, default=0, help="convert only the first N")
    ap.add_argument("--spec-pattern", default=DEFAULT_SPEC_PATTERN)
    args = ap.parse_args()

    if not os.path.isdir(args.root):
        log(f"ROOT is not a directory: {args.root}")
        sys.exit(2)

    session = requests.Session()
    try:
        h = session.get(f"{args.server.rstrip('/')}/health", timeout=10)
        h.raise_for_status()
    except Exception as e:
        log(f"Cannot reach docling-serve at {args.server}: {e}")
        sys.exit(2)
    log(f"Server healthy: {args.server}")

    pdfs = [p for p in find_pdfs(args.root) if not is_spec(p, args.spec_pattern)]
    skipped_specs = len(find_pdfs(args.root)) - len(pdfs)
    if skipped_specs:
        log(f"({skipped_specs} specification(s) left for convert_pdfs.py -- "
            f"pymupdf4llm bold gate)")
    if args.limit:
        pdfs = pdfs[: args.limit]
    if not pdfs:
        log("No non-spec PDFs found")
        sys.exit(2)

    done = skip = failed = 0
    t_run = time.time()
    for i, pdf in enumerate(pdfs, 1):
        md_path = os.path.splitext(pdf)[0] + ".md"
        rel = os.path.relpath(pdf, args.root)
        if already_done(md_path, MARKER):
            skip += 1
            continue
        t0 = time.time()
        try:
            body, tables = convert_remote(session, args.server, pdf, args.api_key)
        except Exception as e:
            failed += 1
            log(f"[{i}/{len(pdfs)}] FAILED  {rel}  -> {e}")
            continue
        stem = os.path.splitext(os.path.basename(pdf))[0]
        md, pages, empty = paginate(body, stem)
        # newline="\n" matches convert_pdfs.py: the corpus is LF, and letting
        # Windows translate to CRLF makes every line differ from a local run
        with open(md_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(md)
        done += 1
        log(f"[{i}/{len(pdfs)}] {rel}  ({len(md)} chars, {pages}p, {empty} empty, "
            f"{md.count('|')} pipes, {tables} tables, {time.time() - t0:.1f}s)")

    log(f"\nDONE converted={done} skipped={skip} failed={failed} "
        f"total={len(pdfs)} in {(time.time() - t_run) / 60:.1f} min")
    log("Now run the real gate:  python convert_pdfs.py <root> --verify")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
