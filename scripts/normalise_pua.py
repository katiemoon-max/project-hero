"""Normalise private-use-area (PUA) glyphs in a converted corpus.

Pearson PDFs embed font subsets whose CMaps map real glyphs into the Unicode
private-use area. Both docling and pymupdf read the same lying CMap, so
re-conversion and cross-engine comparison do NOT recover them (F97) -- the
character arrives as U+F0xx and renders as nothing. That is worse than a gap:
`n -> p + e` becomes `n  p + e`, so a grep for the arrow finds nothing and a
reader sees an absence with no marker that anything was lost.

This is the repair. Mappings below are per-codepoint but were VERIFIED per
(codepoint, font) against the source PDFs -- see EVIDENCE on each row. No
codepoint in the corpora checked so far means different things in different
fonts, and the script asserts that before writing.

Two classes are deliberately NOT mapped:

  FURNITURE   -- margin rules, dotted-line runs and large-bracket/radical
                 construction pieces. They carry no reading meaning, and the
                 bracket pieces cannot be replaced by any single character
                 without misrepresenting the expression they scaffold.
  UNRESOLVED  -- glyphs the SOURCE PDF itself cannot render (they show as tofu
                 in a page render, i.e. absent from the embedded subset). We
                 cannot know what they were, so we do not guess.

Usage:
  python normalise_pua.py <corpus-root> --dry-run     # report only
  python normalise_pua.py <corpus-root>               # rewrite in place

Line endings are preserved byte-for-byte (newline="" on both read and write):
the corpus is LF and a CRLF rewrite would make every line differ from a fresh
conversion.
"""
import argparse
import collections
import glob
import os
import sys

# --- meaning-carrying: substitute -------------------------------------------
# EVIDENCE column records how each was established.
MAPPING = {
    0xF0B7: ("•", "SymbolMT 0xB7; F20 audit 2026-08-07"),          # •
    0xF0FC: ("✓", "Wingdings 0xFC; F20 audit"),                     # ✓
    0xF050: ("✓", "Wingdings2; rendered 2026-08-11"),               # ✓
    0xF053: ("✓", "Wingdings2 + OpenSans; precedes correct MCQ letter in all 14"),
    0xF04F: ("✗", "Wingdings2; rendered 2026-08-11"),               # ✗
    0xF0FB: ("✗", "Wingdings; rendered 2026-08-11"),                # ✗
    0xF097: ("•", "Wingdings2; rendered 2026-08-11 (list bullet)"), # •
    0xF0A3: ("☐", "Wingdings2; rendered 2026-08-11 (tick-box form)"),  # ☐
    0xF079: ("½", "MSReferenceSpecialty; rendered 2026-08-11 -- (KE=)1/2 x 0.42 x 12^2"),
    0xF044: ("Δ", "SymbolMT 0x44"),                                 # Δ
    0xF0B0: ("°", "SymbolMT 0xB0; F20 audit"),                      # °
    0xF071: ("θ", "SymbolMT 0x71; context 'dQ = m x c x d(theta)'"),# θ
    0xF057: ("Ω", "SymbolMT 0x57; context '0.092 kOhm/degC'"),      # Ω
    0xF0AE: ("→", "SymbolMT + OpenSans 0xAE; context 'n -> p + e'"),# →
    0xF06C: ("λ", "OpenSans 0x6C; context 'wavelength / lambda'"),  # λ
    0xF072: ("ρ", "SymbolMT 0x72; context '(rho =) 2680'"),         # ρ
    0xF070: ("π", "OpenSans 0x70; F20 audit; context '4 x pi x D'"),# π
    0xF062: ("β", "SymbolMT 0x62; context 'beta/source'"),          # β
    0xF0BB: ("≈", "SymbolMT 0xBB; context 'ratio 11000:230 i.e. ~48:1'"),  # ≈
    0xF0B4: ("×", "F20 audit"),                                     # ×
    0xF068: ("↑", "F20 audit"),                                     # ↑
    0xF020: (" ",      "F20 audit"),
}

# --- furniture: leave in place ----------------------------------------------
FURNITURE = {
    0xF0A2: "Wingdings2 margin / dotted-line runs (QP cover furniture)",
    0xF0C0: "Wingdings2 furniture",
    0xF0BF: "Wingdings2 furniture",
}
# Adobe Symbol large-bracket / radical construction pieces. Substituting any of
# these with a single character would misstate the expression they draw.
FURNITURE.update({cp: "Symbol large-bracket/radical piece"
                  for cp in range(0xF8E5, 0xF8FF)})

# --- unresolved: the source PDF cannot render these either -------------------
UNRESOLVED = {
    0xF02D: "renders as tofu in the source PDF (absent from the embedded "
            "subset); context 'radiation at the beginning [?] microwaves'",
}


def is_pua(o):
    return 0xE000 <= o <= 0xF8FF


def scan(paths):
    counts = collections.Counter()
    per_file = collections.defaultdict(collections.Counter)
    for p in paths:
        with open(p, "r", encoding="utf-8", newline="") as f:
            t = f.read()
        for ch in t:
            o = ord(ch)
            if is_pua(o):
                counts[o] += 1
                per_file[p][o] += 1
    return counts, per_file


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("root")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not os.path.isdir(args.root):
        print(f"ROOT is not a directory: {args.root}")
        sys.exit(2)

    paths = sorted(glob.glob(os.path.join(args.root, "**", "*.md"), recursive=True))
    counts, per_file = scan(paths)
    if not counts:
        print("No PUA characters found.")
        sys.exit(0)

    mapped = {o: n for o, n in counts.items() if o in MAPPING}
    furn = {o: n for o, n in counts.items() if o in FURNITURE}
    unres = {o: n for o, n in counts.items() if o in UNRESOLVED}
    unknown = {o: n for o, n in counts.items()
               if o not in MAPPING and o not in FURNITURE and o not in UNRESOLVED}

    print(f"{len(per_file)} file(s) carry PUA; {sum(counts.values())} characters\n")
    print(f"  substitutable : {sum(mapped.values()):5d}  ({len(mapped)} codepoints)")
    print(f"  furniture     : {sum(furn.values()):5d}  (left in place)")
    print(f"  unresolved    : {sum(unres.values()):5d}  (source cannot render them)")
    print(f"  UNKNOWN       : {sum(unknown.values()):5d}  ({len(unknown)} codepoints)")
    if unknown:
        print("\n  Unknown codepoints -- verify against a page render before trusting "
              "any file that carries them:")
        for o, n in sorted(unknown.items(), key=lambda x: -x[1]):
            print(f"    U+{o:04X}  x{n}")

    if args.dry_run:
        print("\n(dry run -- nothing written)")
        sys.exit(0)

    changed = 0
    for p in sorted(per_file):
        hits = {o: n for o, n in per_file[p].items() if o in MAPPING}
        if not hits:
            continue
        with open(p, "r", encoding="utf-8", newline="") as f:
            t = f.read()
        for o, (repl, _) in MAPPING.items():
            if o in hits:
                t = t.replace(chr(o), repl)
        # newline="" -> whatever line endings the file had are preserved exactly
        with open(p, "w", encoding="utf-8", newline="") as f:
            f.write(t)
        changed += 1
        detail = ", ".join(f"U+{o:04X}->{MAPPING[o][0]} x{n}" for o, n in sorted(hits.items()))
        print(f"  {os.path.basename(p)[:56]:<56} {detail}")

    print(f"\nrewrote {changed} file(s), {sum(mapped.values())} substitution(s)")


if __name__ == "__main__":
    main()
