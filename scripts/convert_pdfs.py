#!/usr/bin/env python3
"""PDF -> Markdown text-layer extractor for the Project Hero corpus (PyMuPDF, no ML).

Writes <name>.md next to each <name>.pdf under ROOT (recursive). Resumable: skips
files already converted by THIS script (detected via a marker on line 1), and
overwrites .md produced by anything else so the corpus is consistent. Flags
pages/docs with no extractable text (scans), which need OCR or a PDF-direct
fallback — record those in project.json -> corpus.known_casualties.

This is the converter /hero-0-setup §5 kicks off. It is board- and subject-
agnostic: point it at the corpus root and it converts every PDF it finds.

Usage:
  python convert_pdfs.py ROOT                     # convert all PDFs under ROOT
  python convert_pdfs.py ROOT --subdir "Unit 1"   # only one subfolder of ROOT

Requires: pip install pymupdf  (in scripts/requirements.txt)
"""
import sys
import os
import time
import fitz  # PyMuPDF

MARKER = "<!-- pymupdf-extract v1 -->"


def already_done(md_path):
    if not os.path.exists(md_path):
        return False
    try:
        with open(md_path, "r", encoding="utf-8") as f:
            return f.readline().strip() == MARKER
    except Exception:
        return False


def convert(pdf_path):
    stem = os.path.splitext(os.path.basename(pdf_path))[0]
    doc = fitz.open(pdf_path)
    parts = [MARKER, "", f"# {stem}", ""]
    empty_pages = 0
    total_chars = 0
    pages = 0
    for i, page in enumerate(doc, 1):
        pages = i
        txt = page.get_text("text").strip()
        total_chars += len(txt)
        if len(txt) < 20:
            empty_pages += 1
            parts.append(f"## Page {i}\n\n[no extractable text -- likely image/scan]\n")
        else:
            parts.append(f"## Page {i}\n\n{txt}\n")
    doc.close()
    md = "\n".join(parts).rstrip() + "\n"
    return md, total_chars, empty_pages, pages


def main():
    args = list(sys.argv[1:])
    root = None
    subdir = None
    rest = []
    it = iter(args)
    for a in it:
        if a == "--subdir":
            subdir = next(it, None)
        else:
            rest.append(a)
    if rest:
        root = rest[0]
    if not root or not os.path.isdir(root):
        print("Usage: python convert_pdfs.py ROOT [--subdir NAME]")
        print("ROOT must be an existing directory (the corpus root).")
        sys.exit(1)
    search_root = os.path.join(root, subdir) if subdir else root

    pdfs = []
    for dirpath, _, files in os.walk(search_root):
        for fn in files:
            if fn.lower().endswith(".pdf"):
                pdfs.append(os.path.join(dirpath, fn))
    pdfs.sort()

    conv = skip = 0
    no_text_docs = []
    t0 = time.time()
    for p in pdfs:
        md_path = os.path.splitext(p)[0] + ".md"
        if already_done(md_path):
            skip += 1
            continue
        try:
            md, chars, empty, pages = convert(p)
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(md)
            conv += 1
            flag = ""
            if chars < 200:
                no_text_docs.append(p)
                flag = "  <-- NO TEXT (scan?)"
            print(
                f"[{conv:3}] {os.path.relpath(p, root)}  "
                f"({chars} chars, {pages}p, {empty} empty pages){flag}"
            )
        except Exception as e:
            print(f"FAILED {p}: {e}")
    dt = time.time() - t0
    print(f"\nDONE converted={conv} skipped={skip} total={len(pdfs)} in {dt:.1f}s")
    if no_text_docs:
        print(
            f"\n{len(no_text_docs)} docs had ~no extractable text "
            f"(need OCR/PDF-direct fallback -- record in corpus.known_casualties):"
        )
        for d in no_text_docs:
            print("  ", os.path.relpath(d, root))


if __name__ == "__main__":
    main()
