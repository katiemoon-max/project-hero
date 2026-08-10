#!/usr/bin/env python3
"""Second-engine pass over question papers, for figure-borne text.

PACK PROVENANCE: written and production-tested by Leander Oates on 1PH0
(21 papers, 173 s, recovered 3,255 figure-borne tokens). Imported into the
pack 7 Aug 2026 with the corpus root read from project.json instead of the
1PH0 directory layout, and the QP filename filter made an argument.

WHY THIS EXISTS (findings F61/F62/F64, ruling W-31)

The corpus's primary engine is chosen per document type at /hero-0-setup 5.
That choice is correct FOR MARK SCHEMES: a table-aware engine holds the
marking grid together, and a mark scheme is a table.

But docling drops text that boards render INSIDE a figure, and drops it
without leaving a gap. On 1PH0, project.json predicted this in a free-text
note -- "text drawn INSIDE a figure ... may be absent from the converted
markdown" -- and it still reached a student-facing note: a question stem
vanished, the surviving fragment read as a different question, and a false
Higher/Foundation tier claim passed five pipeline stages.

Measured on Paper 1F 2024 June Question paper, docling vs pymupdf4llm:
  docling misses 118 real content tokens (isotopes, cancerous, detectors,
  absorbed, jupiter ...); pymupdf4llm misses 12, all run-together artefacts.
On Paper 1H 2020 November Mark scheme the result INVERTS -- pymupdf4llm misses
31 real guidance words (tangent, curve, labelled, consecutive) plus the
momentum equation symbols m1u1/m2u2/m2v2, and injects Tesseract noise.

So neither engine dominates, and swapping wholesale trades one silent loss for
another. Question papers get a SECOND reading; mark schemes keep the primary
engine only.

Output goes to research/corpus/pdf-second-engine/ mirroring the corpus tree --
never into the corpus itself, so the citable corpus is unchanged and nothing
globbing *.md sees two files per paper. Record the run in project.json ->
corpus.second_engine_pass, and point corpus.content_limitations entries'
mandatory_action at this tree (F65).

HOW TO USE IT: this is the source that settles an ABSENCE claim. Before writing
"no question in the papers does X", or reading a stem that seems to be missing
its question, check the same paper here. pymupdf4llm marks recovered figure
text with <!-- Start of picture text --> ... <!-- End of picture text -->.

Usage: python3 scripts/convert_qp_second_engine.py [--pattern "Question paper"]
The pattern is matched against PDF filenames (substring); set it to the
course's QP naming convention from project.json -> corpus.file_naming.
"""
import argparse
import functools
import json
import pathlib
import sys
import time
import warnings
import logging

# Runs take minutes; a buffered pipe shows nothing until the end (2026-08-10 feedback)
print = functools.partial(print, flush=True)

warnings.filterwarnings("ignore")
logging.disable(logging.INFO)

import pymupdf4llm

ROOT = pathlib.Path(__file__).resolve().parent.parent
CFG = json.loads((ROOT / "project.json").read_text(encoding="utf-8"))
CORPUS = pathlib.Path(CFG["paths"].get("corpus_root") or (ROOT / "research/corpus/pdf"))
if not CORPUS.is_absolute():
    CORPUS = ROOT / CORPUS
OUT = ROOT / "research/corpus/pdf-second-engine"
MARKER = "<!-- pymupdf4llm second-engine pass (F61/F64) -->"


def main():
    # argparse rejects unknown arguments -- the previous hand-rolled parsing
    # silently ignored typos like --patern (2026-08-10 feedback)
    ap = argparse.ArgumentParser(description="Second-engine (pymupdf4llm) pass over question papers, F61/F64.")
    ap.add_argument("--pattern", default="Question paper",
                    help="substring matched against PDF filenames; set from project.json -> corpus.file_naming")
    args = ap.parse_args()
    pattern = args.pattern
    qps = sorted(p for p in CORPUS.rglob("*.pdf") if pattern.lower() in p.stem.lower())
    if not qps:
        # F69 rule: a pass that processed nothing has failed, not passed
        print(f"GATE COULD NOT RUN: no PDFs matching '{pattern}' under {CORPUS}")
        return 2
    print(f"{len(qps)} question papers -> {OUT}\n")
    t0 = time.time()
    for i, pdf in enumerate(qps, 1):
        dest = OUT / pdf.relative_to(CORPUS).with_suffix(".md")
        dest.parent.mkdir(parents=True, exist_ok=True)
        md = pymupdf4llm.to_markdown(str(pdf), show_progress=False)
        dest.write_text(f"{MARKER}\n\n# {pdf.stem}\n\n{md}", encoding="utf-8")
        pics = md.count("<!-- Start of picture text -->")
        print(f"[{i:2}] {pdf.relative_to(CORPUS)}  ({len(md)} chars, {pics} picture-text blocks)")
    print(f"\nDONE {len(qps)} papers in {time.time() - t0:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
