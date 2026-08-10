# Pipeline feedback — defects and improvement candidates

Running log of fresh-eyes findings from real course builds, for triage into repo issues/fixes.
Started 2026-08-10 (consolidating the 2026-08-07 handover list that was never filed). Evidence
citations name the course build that surfaced each item; wording is kept generic to the pipeline.

**Triage pass 2026-08-10 (evening): every open item below addressed in the pack — the
"addressed:" note on each names where. Fixes land from this commit; a build on an older
pull does not have them.**

## From Stage 0 (course onboarding — 2026-08-07, Edexcel IGCSE Physics build)

- [x] **Spec-bold gate passes vacuously when no spec file is present** — should fail loudly
  → addressed: `convert_pdfs.py` now FAILS when zero specs are recognised (same F63/F69
  shape as the zero-mark-schemes case); `--no-spec` asserts a deliberate outside-root spec
- [x] **Scan detector threshold is absolute, not per-page** — long clean PDFs with a few scanned pages slip through
  → addressed: per-page scan check in `convert_pdfs.py` (report-only) — text-bearing files
  with `[no extractable text]` page placeholders are listed with counts, in the JSON too
- [x] **`spec_coverage_gate.py` hard-codes one tracker shape** — needed a text-keyed rewrite for a second course; parameterise column mapping
  → addressed: statement-ID regex + tracker columns (by header text or index, ambiguity
  fails loudly) now read from `project.json` → `spec_coverage`; template block shipped
- [x] **`convert_qp_second_engine.py` ignores unknown args and buffers stdout** — silent arg typos + no live progress
  → addressed: argparse (unknown args reject) + all prints flushed
- [x] **§6 (Cobalt commentary extraction) prompt gaps**: end-note format, part-label charset, multi-paragraph policy, MCQ-explanation classification, per-agent scratch dirs — each produced shard-schema drift that the merge script then had to tolerate
  → addressed: all five specified in the hero-0 §6 prompt schema (`## End notes (not merged)`
  section, lowercase-parenthesised part labels, multi-paragraph line-start rule, MCQ
  explanations excluded from Unwrapped solution commentary, shard-only writes to the project tree)
- [x] **No `nlm doctor`-style pre-flight in §4** (notebook setup) — auth failures surface mid-upload instead of up front
  → addressed: hero-0 §4 step 0 — authenticated NLM call before any notebook work, with the
  `nlm login` / PATH-drop remedies named
- [x] **Converter has no priority/nice option** — a full-corpus conversion monopolises the machine
  → addressed: `convert_pdfs.py --nice` (below-normal priority, Windows + POSIX)

## From Stage 1 wave 1 (research — 2026-08-10, same build)

### Highest impact

- [x] **Formalise the top-up/re-verify stage as `prompts/TOPUP-REVERIFY.md`.** It is the only stage
  with no prompt file (rules live in hero-1 skill text), so the orchestrator hand-writes every brief.
  Its first fresh-context wave yielded: 2 file-swap catches, 6 count corrections (both directions),
  2 superlatives retracted, 5 previously-invisible refs, 1 wrong MS answer intercepted. Standard
  tasks to parameterise: §4 extraction with independent re-verification; §1 quote verification with
  file identity from internal content; count-claim fresh-sweeps.
  → addressed: `templates/prompts/TOPUP-REVERIFY.md` created (tasks A/B/C exactly as above,
  fresh-context requirement, corrections applied in-pack with dated markers + report file);
  hero-1 step 6 now launches it
- [x] **Synoptic-corpus term-index pre-sweep.** Where a course's papers are not unit-scoped ("questions
  may come from any topic area"), every per-subtopic R2 sweeps the whole corpus independently
  (~16 × ~100 files this wave). A single wave-level agent building a per-file hit index for the wave's
  search terms would let R2s start from the index. Est. 30–40% research-cost cut on the ~111
  remaining subtopics of a 127-subtopic course.
  → addressed: hero-1 step 4 — one wave-level agent builds `_term-index-wave<N>.md` before R2s
  launch; index is a lead generator, never an absence authority (absence still needs the direct
  sweep + F62 PDF check); skipped on unit-scoped corpora
- [x] **R3 count-claim semantics.** Add to `R3-local-check.md`: "a sitting count means distinct sittings
  with ER-narrated evidence; MS-note-only legs are listed separately, and an MS quote from a sitting
  already counted is not a further sitting." Most of this wave's count corrections were exactly these
  two conflations. Also port R2's F34 roll-up rule (summaries written FROM the finished list) into R3 —
  every failed superlative this wave originated in an R3 §1.
  → addressed: both now in `R3-local-check.md` §1 (sitting-count semantics + the F34 port);
  TOPUP-REVERIFY task C enforces the same semantics on the fresh-sweep side

### Search hygiene (R2/R3 prompt additions)

- [x] **Sweep equation-symbol forms, not just topic words** — a W = mg question whose MS/ER never
  says "weight" was invisible to every word-based sweep; found only by a symbol-form grep
  → addressed: R2 hard rule + R3 step 2 + TOPUP-REVERIFY standing rules
- [x] **Mandate case-insensitive filename matching** — "Question Paper"/"Question paper" and
  "Mark Scheme"/"Mark scheme" coexist in one corpus; two agents independently hit silent misses
  → addressed: R2 hard rule (with `corpus.file_naming` reconciliation) + R3 + TOPUP-REVERIFY
- [x] **Whitespace-tolerant ER header regex should be the only permitted method** (never enumerate
  forms) — "Question 4 (a)" with a space before the parenthesis still produced one false
  "no ER comment" despite the enumerated-forms rule
  → addressed: R2 + R3 + TOPUP-REVERIFY now say regex-ONLY (`Q\s*<n>\s*\(?` / `Question\s*<n>`
  + content word); the enumerated-forms lists are gone

### Converter / gates

- [x] **Pipe-count table gate passes partial MS row losses.** 10+ verified instances in one wave
  (single marking-point rows/cells dropped or merged while the table still parses). Mechanical
  candidate: cross-check MS per-question row coverage against the QP's "Total for Question N" lines
  → addressed: new `scripts/ms_row_coverage.py` — QP/MS pairing by directory+stem, totalled
  question with zero MS rows = gate FAIL, per-question mark-tally shortfall = report-only lead;
  exits 2 when nothing reconciles (F69); wired into hero-0 §5; smoke-tested on a synthetic pair
- [x] **Superscript concatenation**: "65²" converts to "652" (recurring, multiple sittings) — easy to
  misread as a different number; fix in converter or flag in the conversion report
  → addressed: flagged — `convert_pdfs.py` counts superscripted spans in each source PDF
  (PyMuPDF span flags) and the report lists affected files for PDF verification /
  `content_limitations` recording
- [x] **Widen F62's class definition to mark schemes** — reading-order/row scrambles were scoped to
  QPs in content_limitations; MS-side instances recurred all wave (template fix: ship an MS
  partial-row-loss class in the project.json template's content_limitations)
  → addressed: `mark-scheme partial row loss` entry ships in the project.json template's
  `content_limitations`, mandatory_action pointing at `ms_row_coverage.py` + PDF verification
- [x] **`merge_cobalt_shards.py` invocation mismatch** — hero-1 skill says pass `<project_dir>` but the
  script globs non-recursively at that level; exits 2 when shards live in `research\cobalt-commentary\`
  (the natural home). Glob recursively or default to that subpath
  → addressed: script now falls back to a recursive glob (multi-directory hits fail loudly;
  derived output lands beside the shards); hero-1 note updated — exit 2 now genuinely means
  no shards exist

### Worth keeping exactly as is (positive findings)

- Per-subtopic pipelining (no wave barrier) — wall-clock = slowest chain, not sum of stages
- F68 wave-state verbatim-quote discipline — every downstream ownership/interpretation dispute was
  adjudicated against exact quoted text
- The §1 count-sweep + file-identity-from-content gates — highest verification yield per token in the
  pipeline's history; both defect classes they were built for (file-swap, wrong counts) produced live
  catches on a fresh course

## Wave 1 writing pilot — 4PH1 (2026-08-10)

The two-writer pilot surfaced **five both-compliant divergence axes** (the prompt-gap mechanism
worked as designed). Creator-ratified rulings, four upstreamed into `templates/prompts/WRITER.md`
same day:

- [x] **Format-block labels are descriptive task labels, never bare command words** (chunk-heading
  self-explanatory rule)
- [x] **Exam-section Example refs carry the full part reference** (the block quotes one part's
  scheme) **+ paper code on courses with same-series paper variants** (1P/1PR made bare refs
  ambiguous)
- [x] **Worked-example anatomy: narrative default, verbatim-bank blockquote form for multi-point
  ("any N from" / ~4+) schemes** — hybrid ruling, both pilot forms sanctioned with a trigger
- [x] **Zero overlap between worked examples and format-block Examples** where evidence allows;
  different-parts reuse only on thin SPs
- Course-specific (README only): depth range 250–600 words per key-concept H3; board unit
  notation (m/s, m/s²) outranks the house negative-exponent default — the units principle is now
  stated generically in WRITER.md's house-style line
- Observation for future pilots: both writers independently converged on the board-notation units
  deviation and flagged it unprompted — the pilot's "surface your silent choices" instruction (F33)
  is earning its place

*(The four WRITER.md rulings were sitting uncommitted on disk when this triage ran — committed
2026-08-10 so a re-pull actually carries them.)*
