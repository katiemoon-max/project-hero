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
laptop, or the same PDF converts differently on the two machines. This client
needs docling-core at that same pin too: export_to_markdown() runs HERE, so the
client's version -- not the server's -- decides the bytes we write.

WHY ASYNC -- the synchronous /v1/convert/file gives up at
DOCLING_SERVE_MAX_SYNC_WAIT (default 120s) and returns 504, no matter how
patient the client is. A spare machine is by definition the slow one: measured
135s for a 15-page mark scheme and 293s for a 28-page one, so every real
conversion failed. We submit to the queue instead and long-poll for the result,
which has no wall-clock ceiling and is what makes --concurrency possible.

Usage:
  set HERO_DOCLING_API_KEY=<key>
  python remote_convert.py <corpus-root> --server http://<host>:5001 [--limit N]
                           [--concurrency N]

Verify afterwards with the real gate:
  python convert_pdfs.py <corpus-root> --verify
"""
import argparse
import concurrent.futures as cf
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

TIMEOUT_S = 1800      # per-HTTP-request ceiling
POLL_WAIT_S = 30      # server-side long-poll window per status call
JOB_TIMEOUT_S = 7200  # give up on a single queued job after this

# Must match convert_pdfs.py's local pipeline exactly -- see module docstring.
CONVERT_OPTIONS = [
    ("to_formats", "json"),
    ("do_ocr", "false"),
    ("do_table_structure", "true"),
    ("table_cell_matching", "true"),
    ("do_formula_enrichment", "false"),
    ("pdf_backend", "pypdfium2"),
    ("include_images", "false"),
    ("table_mode", "accurate"),
]


def _unauthorised(r):
    if r.status_code == 401:
        raise RuntimeError("401 from server -- API key missing or wrong "
                           "(set HERO_DOCLING_API_KEY, or --api-key)")


def _submit(session, server, pdf_path, headers):
    """Enqueue one PDF, return its task_id."""
    with open(pdf_path, "rb") as fh:
        files = {"files": (os.path.basename(pdf_path), fh, "application/pdf")}
        r = session.post(f"{server}/v1/convert/file/async", files=files,
                         data=CONVERT_OPTIONS, headers=headers, timeout=TIMEOUT_S)
    _unauthorised(r)
    r.raise_for_status()
    task_id = r.json().get("task_id")
    if not task_id:
        raise RuntimeError("server accepted the upload but returned no task_id")
    return task_id


def _await_task(session, server, task_id, headers):
    """Long-poll until the task leaves pending/started. Returns the final status."""
    deadline = time.time() + JOB_TIMEOUT_S
    while True:
        # `wait` blocks server-side, so this is a long-poll and not a busy loop.
        r = session.get(f"{server}/v1/status/poll/{task_id}",
                        params={"wait": POLL_WAIT_S}, headers=headers,
                        timeout=POLL_WAIT_S + 60)
        _unauthorised(r)
        r.raise_for_status()
        status = r.json()
        if status.get("task_status") in ("success", "failure"):
            return status
        if time.time() > deadline:
            raise RuntimeError(f"task {task_id} still "
                               f"{status.get('task_status')} after {JOB_TIMEOUT_S}s")


def convert_remote(session, server, pdf_path, api_key):
    """Queue one PDF, wait for it, return (markdown_body, n_tables)."""
    from docling_core.types.doc.document import DoclingDocument

    server = server.rstrip("/")
    headers = {"X-Api-Key": api_key} if api_key else {}

    task_id = _submit(session, server, pdf_path, headers)
    final = _await_task(session, server, task_id, headers)
    if final.get("task_status") != "success":
        raise RuntimeError(f"task {task_id} failed: "
                           f"{final.get('error_message') or final.get('failure')}")

    r = session.get(f"{server}/v1/result/{task_id}", headers=headers,
                    timeout=TIMEOUT_S)
    _unauthorised(r)
    r.raise_for_status()
    payload = r.json()
    if payload.get("status") not in ("success", "partial_success"):
        raise RuntimeError(f"server status={payload.get('status')} "
                           f"errors={payload.get('errors')}")

    doc = DoclingDocument.model_validate(payload["document"]["json_content"])
    body = doc.export_to_markdown(page_break_placeholder=PAGE_BREAK,
                                  compact_tables=True)
    return body, len(getattr(doc, "tables", []) or [])


def process_one(pdf, server, api_key):
    """Convert one PDF and write its .md. Runs in a worker thread."""
    t0 = time.time()
    # A Session per job: requests.Session is not documented as thread-safe, and
    # the setup cost is noise next to a multi-minute conversion.
    session = requests.Session()
    try:
        body, tables = convert_remote(session, server, pdf, api_key)
    finally:
        session.close()
    stem = os.path.splitext(os.path.basename(pdf))[0]
    md, pages, empty = paginate(body, stem)
    # newline="\n" matches convert_pdfs.py: the corpus is LF, and letting
    # Windows translate to CRLF makes every line differ from a local run
    with open(os.path.splitext(pdf)[0] + ".md", "w",
              encoding="utf-8", newline="\n") as f:
        f.write(md)
    return len(md), pages, empty, md.count("|"), tables, time.time() - t0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("root", help="corpus root (an existing directory)")
    ap.add_argument("--server", required=True, help="e.g. http://192.168.1.42:5001")
    ap.add_argument("--api-key", default=os.environ.get("HERO_DOCLING_API_KEY", ""))
    ap.add_argument("--limit", type=int, default=0, help="convert only the first N")
    ap.add_argument("--concurrency", type=int, default=1,
                    help="PDFs in flight at once (default 1). The server runs "
                         "DOCLING_SERVE_ENG_LOC_NUM_WORKERS (default 2), so "
                         "more than that only lengthens the queue. Each worker "
                         "loads its own models unless the server sets "
                         "DOCLING_SERVE_ENG_LOC_SHARE_MODELS=true -- raise this "
                         "only if the box has the RAM headroom.")
    ap.add_argument("--spec-pattern", default=DEFAULT_SPEC_PATTERN)
    args = ap.parse_args()

    if not os.path.isdir(args.root):
        log(f"ROOT is not a directory: {args.root}")
        sys.exit(2)
    if args.concurrency < 1:
        log("--concurrency must be at least 1")
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

    todo = []
    skip = 0
    for pdf in pdfs:
        if already_done(os.path.splitext(pdf)[0] + ".md", MARKER):
            skip += 1
        else:
            todo.append(pdf)

    done = failed = 0
    t_run = time.time()
    if todo and args.concurrency > 1:
        log(f"Queueing {len(todo)} PDF(s), {args.concurrency} in flight")
    with cf.ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        futures = {pool.submit(process_one, pdf, args.server, args.api_key): pdf
                   for pdf in todo}
        # as_completed, so a slow PDF never holds up reporting of the others
        for n, fut in enumerate(cf.as_completed(futures), 1):
            rel = os.path.relpath(futures[fut], args.root)
            try:
                chars, pages, empty, pipes, tables, dt = fut.result()
            except Exception as e:
                failed += 1
                log(f"[{n}/{len(todo)}] FAILED  {rel}  -> {e}")
                continue
            done += 1
            log(f"[{n}/{len(todo)}] {rel}  ({chars} chars, {pages}p, {empty} empty, "
                f"{pipes} pipes, {tables} tables, {dt:.1f}s)")

    log(f"\nDONE converted={done} skipped={skip} failed={failed} "
        f"total={len(pdfs)} in {(time.time() - t_run) / 60:.1f} min")
    log("Now run the real gate:  python convert_pdfs.py <root> --verify")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
