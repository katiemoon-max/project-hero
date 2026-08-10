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

## From Stage 3 re-audit + Stage 4 publish (2026-08-10 evening, Edexcel IGCSE Physics build — wave 1 shipped end-to-end)

### Script defects

- [ ] **`strip_for_cobalt.py` argv is `[src, dst]` — a multi-file call silently clobbers the second file** with the stripped content of the first (overwrote a verified master; recovered from git, which is the only reason it was cheap). Fix: accept many files / a directory, and REFUSE to write any destination that exists as a non-`.cobalt` master.
- [ ] **Markdown table cell-splitting via `str.strip('|')` eats ALL boundary pipes**, deleting an empty first cell — every continuation row orphans, statements truncate ("2.20 know that:"), and truncated blobs become containment WILDCARDS that steal text-join allocations (9 misallocations from 2 truncations). The original `spec_coverage_gate.py` has this same parse; fix is one-pipe-per-side splitting. Found while adapting the gate for 4PH1.
- [ ] **Spec statement shapes the coverage-gate parser must handle beyond tables** (all present in the pymupdf4llm 4PH1 spec): fused multi-statement PROSE lines (1.3–1.10 on one line); statements inside PICTURE-TEXT blocks with `<br>` separators (whole of section 5(b)); bullets; singular "use the following unit"; table continuation rows. A monotonic statement-id filter guards decimals-in-text; 3-token split tracker rows need a specificity tie-break (shortest matching statement). Working adaptation: the build's `scripts/spec_coverage_gate_4ph1.py` — fold what generalises into the parameterised gate.
- [ ] **`project.json` path fields must be PURE paths** — a glued human annotation inside `paths.syllabus_cross_check` broke the gate's file open. Convention adopted: companion `_note` field carries the prose. Worth a loud validation in any script reading a path from project.json.
- [ ] **`fixer_diff_sweep.py` crashes printing U+2212 on cp1252 consoles** (workaround `PYTHONIOENCODING=utf-8`) — carried from the morning session in case not yet filed.

### Process findings

- [ ] **F55 cost-model data point:** a wave given a full check+fix cycle AND pack patches BEFORE the blind re-audit yielded 1.7 blockers/file blind (27B/68F/0 anomalies over 16 files) vs ~10–13 on both prior builds' blind passes — the prior cycle cuts blind yield ~6x, yet blindness still surfaced ≥1 blocker in 12 of 16 signed-off files INCLUDING both creator-ratified pilot exemplars. Blindness stays the active ingredient; the cheap pass first makes the expensive pass sharper.
- [ ] **Silent in-quote correction of board typos is a RECURRING writer failure mode** — 2 of 2 pilot exemplars did it ("less that", "eroneous"), and both packs had ALSO silently corrected the same typos inside verbatim blocks. WRITER/CHECKER emphasis + extend quote-integrity sweeps to pack verbatim blocks.
- [ ] **Spec-quote glyph fidelity is a class check, not a per-file eyeball** — the spec prints U+2212 in "velocity−time"; drafts and both exemplars had U+2013; one re-auditor caught its file, MISSED two instances in another, and the mechanical class back-sweep (F51) caught what the per-file audit didn't. Add a glyph-compare of spec quotes against the converted spec to the checker's mechanical sweeps.
- [ ] **Corpus retention needs a stage-0 agreement with the creator** — the course's 149 source PDFs were Explorer-deleted mid-build (archive reorganisation); recovered from the Recycle Bin, and four in-flight agents fell back to page dumps/converted-md/external mirrors meanwhile (all later re-verified at the restored originals). The pipeline's PDF-verification spine assumes the PDFs stay put until course close — say so explicitly at hero-0 and record where the corpus lives.
- [ ] **Read-back query phrasing (F73 refinement):** at `min_score 0.01` an isolated bullet string can rank below an adjacent chunk — include the section-heading text alongside the target string, or raise `limit` and assert across the top hits. All 16 wave-1 read-backs verified; three needed the raised-limit path.
- [ ] **Zero-MCQ sanctioned absence pattern ratified** (course-owner ruling) and now in `templates/prompts/WRITER.md` — state the format context, the absence, and the near-miss; never fabricate sub-blocks, never improvise per file.
