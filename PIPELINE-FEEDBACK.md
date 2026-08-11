# Pipeline feedback — defects and improvement candidates

Running log of fresh-eyes findings from real course builds, for triage into repo issues/fixes.
Started 2026-08-10 (consolidating the 2026-08-07 handover list that was never filed). Evidence
citations name the course build that surfaced each item; wording is kept generic to the pipeline.

**Triage pass 2026-08-10 (evening): every open item below addressed in the pack — the
"addressed:" note on each names where. Fixes land from this commit; a build on an older
pull does not have them.**

**Triage pass 2026-08-11: the stage 3 re-audit + stage 4 publish section (filed 2026-08-10
evening as a log-only commit) is now implemented — scripts, prompts, skills and template;
each item's "addressed:" note names where. Same re-pull caveat.**

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

- [x] **`strip_for_cobalt.py` argv is `[src, dst]` — a multi-file call silently clobbers the second file** with the stripped content of the first (overwrote a verified master; recovered from git, which is the only reason it was cheap). Fix: accept many files / a directory, and REFUSE to write any destination that exists as a non-`.cobalt` master.
  → addressed: argparse rewrite — many files and/or directories, each writing its own
  `.cobalt.md` sibling; `-o` restricted to exactly one input file; ALL destinations
  validated before ANY write, and any destination that is not `.cobalt.md` is refused
  (already-stripped inputs refused too). The exact old clobber call now exits 1 before
  touching disk — exercised. hero-4 step 3 documents the new shape
- [x] **Markdown table cell-splitting via `str.strip('|')` eats ALL boundary pipes**, deleting an empty first cell — every continuation row orphans, statements truncate ("2.20 know that:"), and truncated blobs become containment WILDCARDS that steal text-join allocations (9 misallocations from 2 truncations). The original `spec_coverage_gate.py` has this same parse; fix is one-pipe-per-side splitting. Found while adapting the gate for 4PH1.
  → addressed: `split_row()` in `spec_coverage_gate.py` splits exactly one boundary pipe
  per side; continuation rows (empty first cell, text in later cells) now CONTINUE the
  previous statement instead of orphaning — smoke-tested on a synthetic spec with a
  split-across-rows statement, covered in full
- [x] **Spec statement shapes the coverage-gate parser must handle beyond tables** (all present in the pymupdf4llm 4PH1 spec): fused multi-statement PROSE lines (1.3–1.10 on one line); statements inside PICTURE-TEXT blocks with `<br>` separators (whole of section 5(b)); bullets; singular "use the following unit"; table continuation rows. A monotonic statement-id filter guards decimals-in-text; 3-token split tracker rows need a specificity tie-break (shortest matching statement). Working adaptation: the build's `scripts/spec_coverage_gate_4ph1.py` — fold what generalises into the parameterised gate.
  → addressed: folded into the parameterised gate as config — `statement_shapes`
  (`"prose"` enables fused-prose/bullet/picture-text parsing with `<br>` normalisation,
  guarded by the monotonic-id filter), `bounds` (statement-region regexes),
  `unallocated_whitelist_regex` (covers singular/plural "use the following unit(s)"
  rulings, checks A/D only, never C) and `tier_from_bold: false` (loud SKIP of check B
  for courses whose tier source is not PDF bold). Defaults reproduce 1PH0; both modes
  smoke-tested (decoy decimals not parsed, appendix bounded out). The text-keyed
  tracker join + shortest-statement tie-break does NOT generalise (the pack gate is
  id-keyed) — the 4PH1 adaptation stays the reference for id-less trackers, named in
  the gate docstring and the template comment
- [x] **`project.json` path fields must be PURE paths** — a glued human annotation inside `paths.syllabus_cross_check` broke the gate's file open. Convention adopted: companion `_note` field carries the prose. Worth a loud validation in any script reading a path from project.json.
  → addressed: `cfg_path()` in `spec_coverage_gate.py` — fails loudly on a missing,
  non-string, whitespace-wrapped or unresolvable path value, naming the `<key>_note`
  convention in the error (tested: an annotated value exits 1 with the remedy printed);
  the convention itself now leads the template's `paths` block as its `_comment`
- [x] **`fixer_diff_sweep.py` crashes printing U+2212 on cp1252 consoles** (workaround `PYTHONIOENCODING=utf-8`) — carried from the morning session in case not yet filed.
  → addressed: stdout/stderr reconfigured to utf-8 (`errors="replace"`) at the top of
  `main()` — no per-run env var needed; same guard added to `spec_coverage_gate.py`,
  which also prints source glyphs. Tested printing a live U+2212 line

### Process findings

- [x] **F55 cost-model data point:** a wave given a full check+fix cycle AND pack patches BEFORE the blind re-audit yielded 1.7 blockers/file blind (27B/68F/0 anomalies over 16 files) vs ~10–13 on both prior builds' blind passes — the prior cycle cuts blind yield ~6x, yet blindness still surfaced ≥1 blocker in 12 of 16 signed-off files INCLUDING both creator-ratified pilot exemplars. Blindness stays the active ingredient; the cheap pass first makes the expensive pass sharper.
  → addressed: recorded in hero-3 step 5 as the third F55 data point, with the reading
  spelled out (cheap cycle first is not redundant with blindness — it sharpens it)
- [x] **Silent in-quote correction of board typos is a RECURRING writer failure mode** — 2 of 2 pilot exemplars did it ("less that", "eroneous"), and both packs had ALSO silently corrected the same typos inside verbatim blocks. WRITER/CHECKER emphasis + extend quote-integrity sweeps to pack verbatim blocks.
  → addressed: WRITER quote-integrity rule 1 and CHECKER item 6 both carry the
  recurrence warning ("the itch to fix is precisely the failure"; a pack-matching quote
  can still be wrong against the board — verify clean-looking quotes at the SOURCE);
  TOPUP-REVERIFY standing rules now extend quote integrity to the pack's own verbatim
  blocks — board typos the pack silently fixed are RESTORED with a dated marker
- [x] **Spec-quote glyph fidelity is a class check, not a per-file eyeball** — the spec prints U+2212 in "velocity−time"; drafts and both exemplars had U+2013; one re-auditor caught its file, MISSED two instances in another, and the mechanical class back-sweep (F51) caught what the per-file audit didn't. Add a glyph-compare of spec quotes against the converted spec to the checker's mechanical sweeps.
  → addressed: CHECKER item 2 — mechanical character-level compare of every spec quote
  against the converted spec, look-alike table named (−/–/-, ×/x, ∆/Δ), one instance
  triggers a whole-file sweep of the class
- [x] **Corpus retention needs a stage-0 agreement with the creator** — the course's 149 source PDFs were Explorer-deleted mid-build (archive reorganisation); recovered from the Recycle Bin, and four in-flight agents fell back to page dumps/converted-md/external mirrors meanwhile (all later re-verified at the restored originals). The pipeline's PDF-verification spine assumes the PDFs stay put until course close — say so explicitly at hero-0 and record where the corpus lives.
  → addressed: hero-0 §3 step 4 — explicit agreement with the user that the corpus
  location is frozen until course close (or a move protocol agreed), recorded with date
  in the new `corpus.retention_agreement` template field
- [x] **Read-back query phrasing (F73 refinement):** at `min_score 0.01` an isolated bullet string can rank below an adjacent chunk — include the section-heading text alongside the target string, or raise `limit` and assert across the top hits. All 16 wave-1 read-backs verified; three needed the raised-limit path.
  → addressed: hero-4 step 9, ahead of the investigate-never-re-issue rule — heading
  text alongside the target string, or raised `limit` asserting across top hits
- [x] **Zero-MCQ sanctioned absence pattern ratified** (course-owner ruling) and now in `templates/prompts/WRITER.md` — state the format context, the absence, and the near-miss; never fabricate sub-blocks, never improvise per file.
  → addressed: already landed in WRITER.md's exam-section rules (commit 4485fb3) —
  verified present; ticked for the record

## Round 7 — 1PH0 findings F67–F113 + wave-2 check stage F117–F122 (triaged 2026-08-11)

Source: `project-hero-F67-F113-2026-08-11.md` and `project-hero-F117-F122-2026-08-11.md`
(Leander Oates, 1PH0 build; standalone extracts of `FINDINGS-FOR-KATIE-3.md`). Assessed and
fixed against the pack at `94b96f7`. Same re-pull caveat as prior rounds — AND note F76 below:
a re-pull alone updates nothing in an existing project; the project's `prompts/`/`scripts/`
copies must be refreshed deliberately.

### Closed without pack action

- [x] **F67** — withdrawn by Leander (∆ codepoint; render test beats convention). `preflight_sweep.py`'s
  message already carries the render-test evidence since round 6
- [x] **F68–F71, F73, F74, F100 (template half)** — confirmed fixed at `9f255f3` by Leander's own
  mechanical re-verification; nothing further owed
- [x] **F69 (residual: partial-sweep silence)** — already fixed before this round:
  `protect_starred_refs.py` and `verify_starred_refs.py` sweep ALL arguments recursively and cite F69;
  Leander's retest predates the fix (it ran at `b17da98`)
- [x] **F72 — CLOSED AGAIN, scoping works; do NOT escalate to the Cobalt team.** Re-opened 11 Aug on
  all-null leaf read-backs; disproven same day by direct test on the re-issued
  `doc_Y6xwXPYsmGCDSGf6`: `return_type: "subtopic"` → `sbt_MTSYCSv8JbgdqS8P` bound (the exact id in
  `cobalt-structure.json`), `return_type: "spec_point"` → `spcpt_sV2vmcp4GCWPCCR7` bound. Null ids on
  the `generic` leaf are DESIGNED (scope lives on typed ancestor chunks built from the document's own
  headings); step 9's read-back spec says `no return_type`, so its nulls prove nothing. The 7 Aug
  withdrawal was right both times.
  → addressed: hero-4 step 9 now records this permanently, incl. "never assert non-null scope ids
  on the leaf read-back — that gate would fail every correctly-scoped document"
- [x] **F89** — moot: README.md carries no `Q*17` exemplar at this commit (Leander's own status note
  said unconfirmed; grep confirms absent)
- [x] **F112** — reserved, never raised; no action possible

### Addressed this round

- [x] **F75** (strip backstop vs checker title precedence) → hero-3 step 3: backstop is for callouts
  no checker saw; a wave with an open check does not strip
- [x] **F76** (pack re-pull updates nothing in the project) → `project.json` → `pack_commit` (template
  + hero-0 §8), `PACK PROVENANCE` header convention, and a pack-freshness precondition in hero-2
- [x] **F78 + F86** (WRITER exemplar vs CHECKER item 8 — **ruling: item 8 is the intent**) →
  WRITER.md:30 exemplar now `Q6(b)(i)` (Leander's mark-scheme-verified part division) with the
  main-number-alone-is-not-a-reference rule + the bare-invented-example carve-out defended; CHECKER
  item 8 reworded from "headings" to "bold label lines" (the artefact the pack actually emits) with
  the same carve-out. 1PH0's local WRITER.md fix is superseded by the pack version on next refresh.
  **Wave-1 cost note: 1PH0's 42 part-less worked-example labels are a fix batch needing per-item
  source lookups; the 45 starred refs resolve mechanically from ms-extracts (69 part-bearing hits upstream)**
- [x] **F79** (rulings have no work-item mechanism) → hero-3 step 2: mandatory `Files swept:` line
  enumerating all N masters with per-file verdicts; \<N entries = incomplete, mechanically checkable
- [x] **F80** (item 21 caught none of four adjacent refutations) → CHECKER item 21 is now mechanical:
  restate the count arithmetic in the report, passes included
- [x] **F82** (brief/prompt precedence — 16 agents, 4 resolutions) → CHECKER output: format = this
  file wins; what-to-check = brief additive
- [x] **F83** (narrow pass overwrote hero-metrics; 8+ blockers vanished) → CHECKER: append
  `pass=`-tagged line, never overwrite; hero-3: sum untagged lines + cross-check against `### B`
  heading count
- [x] **F84** (nothing verifies arithmetic inside a prescription) → CHECKER F54 rule: recompute every
  numeric result, state it in the finding, name rounded-source divergence, hold replacements to every
  content rule incl. stem-prescribed methods. *(Script half — numeric-equality flag in
  fixer_diff_sweep — still open, below)*
- [x] **F85** (verify_starred_refs certified the defect) → script rewritten: `Q*n` = DEFECT (exit 1),
  part-form `Qn(x)*` render-checked, `--min-ref-lines` floor for the zero-match no-op case; the
  defective exemplar also purged from WRITER.md:54, CHECKER item 13 and R2. Smoke-tested: catches
  the defect form, the escape forms, and the star-eaten-by-bold case
- [x] **F87** (Windows paths pack-wide) → 15 `<RESEARCH_DIR>\`/`<CORPUS_DIR>\` lines across 7 prompt
  files → forward slashes; zero backslash placeholders remain
- [x] **F88** (`rn.md` required with no producing step) → WRITER.md marks it conditional (RN-bearing
  courses only; missing-on-RN-course = report, never silently absorb); hero-0 §6.6 names the
  producing step (`findRevisionNote` per subtopic) or a dated `paths.rn_source: null` ruling
- [x] **F90** (verify_starred_refs.py wired into nothing) → hero-4 gate 1, directly after the protect
  step, exit 2 = step not satisfied
- [x] **F91** (grid corrupted by 17 concurrent writers) → orchestrator owns the grid; agents report in
  return messages and never write the state file (hero-3 bookkeeping + hero-2 W-marking + brief-footer
  instruction)
- [x] **F92** (11 of 17 fixers logged nothing; 3 date formats) → FIXER.md: `## Fixes applied — YYYY-MM-DD`
  ISO, MANDATORY even on clean runs; hero-3's `F` derivation note carries the failure mode
- [x] **F93** (fixer failure modes invisible from the orchestrator's seat) → hero-3 step 3: work lists
  carry the EXPECTED POST-FIX STRING per item; completion = grep for it. (The dead-fixer warning was
  already load-bearing and is untouched)
- [x] **F94** (levelled locator fails on this course) → R2: indicative-content block is the
  authoritative signal; asterisk demoted to corroborating hint; ref-typography tolerance rule added
- [x] **F95** (seven dead items dispatched against a live doc) → FIXER.md: live-documents uncertainty
  rule (UNRESOLVED, never a plausible edit) + superseded-finding check against wave-state rulings;
  hero-3: overturn-sweep rule (strike dead findings in the reports, at the item, with the ruling id),
  `depends-on: W-<n>` lines, stale-report flag at fixer dispatch
- [x] **F97 (downstream half)** (invisible PUA glyphs pass every gate) → `preflight_sweep.py`: any
  U+E000–F8FF character is a FAIL, tabulated per codepoint (never aggregate); hero-4 gate 2 names it.
  *(Stage-0 normalisation + other-course sweeps still open, below)*
- [x] **F99** (casualties list goes stale as a certificate of health) → R2: register is append-only
  and agent-writable; absence from it is not evidence
- [x] **F100 (prompt half)** (missing key read as "no limitations") → R3 both variants: absent ≠ empty;
  a missing key is a setup defect to report
- [x] **F102** (back-sweep detector couldn't detect its own defect; `\b9` bug made 32 false gaps) →
  hero-3: every mechanical gate validated by FALSIFICATION before its clean run is trusted; format
  coverage stated
- [x] **F103** (six of six damage claims false) → R2: damage claims carry the burden of proof — fresh
  narrow re-read, structural evidence inadmissible, upstream claims don't close the question;
  claim vocabulary now flagged by preflight for the wave sweep
- [x] **F104** (every false absence proved against a proxy) → R2: absence rows may cite only evidence
  the content cannot avoid having (the MS's marking points, read); tier-twin check mandatory
- [x] **F105** (§4 unusable as a work-list) → R3 both variants: per-ref disposition
  (`GAP`/`CONFIRMED`), `**None.**` heading when all confirmatory
- [x] **F106** (false "no PDFs exist" disabled the court of last resort) → R3: existence claims
  recursive + command printed; restatement ≠ check; hero-0: counted recursive `corpus.inventory` as
  the authority; hero-3 step 7 sweeps infrastructure claims FIRST
- [x] **F107 + F109 (rule halves)** ("lost in conversion" names a process; a glyph left no text trace) →
  R2/R3: three verification routes (second-engine tree → PDF text layer → RENDERED page image),
  routes-tried list required for any unrecoverable claim, "symbol — reproduce as description";
  preflight flags the claim vocabulary. *(Script halves open, below)*
- [x] **F108** (a 2-constraint fit "confirmed" 3 unknowns) → R2: constraint-counting rule
  (under-determined = candidate + anomaly, never confirmed), distractor rationale/tolerance bands as
  first-class evidence, per-point converter re-test, `INFERRED —` prefix never inheriting a VERBATIM label
- [x] **F111** (a missing binary reported as environment; two notes corroborating in a circle) → R2:
  a blocker names a capability with alternatives tried; grounding terminates at a paper; hero-3 blind
  re-audit note "check the method even when the answer is right" carried in step 7's sweep rule
- [x] **F113** (record gap — the three asks, all taken) → (1) hero-3 step 5 writes its own dated
  completion record into the wave-state file; (2) `/hero` derives re-audit state and machine-checkable
  blockers from the disk; (3) template `status` block: dated blockers, checkable-checked discipline
- [x] **F117 (rule half)** (spec quotes corrupt hyphenated compounds inconsistently) → WRITER quote-integrity
  rule 2: converted spec FINDS a statement, never QUOTES one; compound terms verified at the spec PDF.
  *(Gate script open, below)*
- [x] **F118** (alias licence over-granted at file scope) → CHECKER item 23: the licence is held by a
  spec point; check which `## Spec Point:` block the citation sits under
- [x] **F119** (command-word reference quote flagged as paper-scope evidence) → CHECKER item 22:
  reference-traceable quotations exempt; grep the reference dir before any paper-scope blocker
- [x] **F120** (unbounded quantifiers read as confident prose) → CHECKER item 16 three-way grading +
  `preflight_sweep.py` report-only regex
- [x] **F121 (pointer half)** (brief names a file the tier flag is not in) → hero-2: verify file+field
  on THIS project before writing the brief; boolean insufficiency routed to the existing
  `"partial"` + note shape *(1PH0-side: move 2.31 to `"partial"` per the W-55 escalation)*
- [x] **F122(1)** — 1PH0 briefing corrections, done on the project by Leander; **F122(3)** = F115, open below
- [x] **Wave-close claims sweep** (the batch's structural ask: five defect classes, one discovery
  route, zero detectors) → hero-3 NEW step 7 — all absence/damage/infrastructure claims read together
  against the other files' extractions and stage 0's inventory, infrastructure first

### Open — needs Katie's decision or a build

- [ ] **F77** — Leander's judgement call: `convert_qp_second_engine.py` left un-refreshed to preserve
  the provenance of a finished corpus. **Recommend: accept the deviation** (the artefact and its
  producer should agree) and formalise via the now-conventional `PACK PROVENANCE` header — needs
  Katie's word to Leander either way
- [ ] **F81** — cross-file distribution sweep (histogram of shape-bearing features across a wave, no
  pass/fail; the only structural detector for 100%-consistent defects like F70's 227/227). Small
  build; complements the hero-3 step 7 claims sweep
- [ ] **F84 (script half)** — `fixer_diff_sweep.py`: flag fixer-added lines carrying `=` between two
  evaluable numeric expressions, report-only
- [ ] **F96** — duplicate-SP detection: run the match test on the STATEMENT (record match class:
  identical/superset/fragment/body-only; only identical auto-admits), add a third category
  `statement_family` (general statement + context-bound instances — write every instance), state
  "a superset is never a duplicate of its subset". Design decision on the sp-mapping shape — Katie
- [ ] **F97 (stage-0 half)** — PUA normalisation in the converter (strip `0xF000`, read remainder as
  Adobe Symbol, `[?U+XXXX]` for unmapped, skip Wingdings) — the ONLY workable remedy (re-conversion
  and cross-engine comparison both read the same lying CMap). **Plus: sweep every OTHER Pearson-PDF
  course this pipeline has converted (IAL export's 222 live docs, 4PH1) with the damage-side sweep —
  masters' quoted lines vs repaired corpus — not the defect-side grep, which finds nothing downstream**
- [ ] **F98** — stage 0 emits the second-engine tree's per-document-type manifest; cross-check rules
  state their coverage ("QPs only on this course — MS/ER go straight to the PDF")
- [ ] **F101 (residual)** — orchestrator-authored register entries carry inline evidence, verified at
  the named line range before writing (the claims sweep now catches these late; this writes them
  right at the source)
- [ ] **F107/F109/F110 (script halves)** — adopt 1PH0's `page_drop_sweep.py` (with its positive +
  negative controls) and the QP-only double-space sweep into the pack's stage-0 conversion report;
  plus F110's measured-figure provenance rule (script in repo, controls stated, discarded detectors
  recorded) as pack policy for any self-computed number
- [ ] **F115 / F122(3)** — `spec_coverage_gate.py`: wave-scoped verdict. Design: failures grouped by
  the tracker's wave/unit allocation; in-wave failures exit non-zero, out-of-wave debt prints as a
  separate REPORT block ("this wave clear; course debt: N statements in waves 2+") — never a bare
  GATE FAILED the agent has to read raw detail to interpret
- [ ] **F117 (gate half)** — a script comparing each `## Spec Point:` statement quotation against the
  spec PDF text, exact-match after whitespace normalisation (statement numbers known, one file;
  sections 6/10/13 will hit the corrupted compounds still sitting in 1PH0's converted spec)
- [ ] **F122(2)** — star/bold adjacent-incompatibility (`**…Q9(c)***` — closing bold eats the star).
  Detection now ships in both starred-ref scripts; the CONVENTION (star outside the bold vs bolded
  citations drop the star) is Katie's call, then one line in WRITER/CHECKER

## Corpus conversion — CPU cost and remote offload (2026-08-11, Edexcel IGCSE + GCSE Physics)

Measured on an i5-1235U (2 P-cores + 8 E-cores = 12 logical) and a spare Ryzen 5 3500U (4C/8T,
6.9 GB). Reference workload: 38-page Edexcel mark scheme; corpus scale 149 PDFs / 3,734 pages.
Every row below was verified byte-for-byte against the committed 4PH1 corpus.

### Conversion cost

- [x] **`--nice` does not reduce CPU; thread oversubscription on hybrid CPUs does** — the 2026-08-07
  `--nice` item treated priority as the remedy, but priority alone measures 5% (inside run-to-run
  noise). docling schedules ~10 threads across fast P-cores and slow E-cores and burns CPU
  spin-waiting. Affinity is the actual lever: pinning to the first 4 logical CPUs cut CPU 37%
  (611 → 383 CPU-s) with **no wall-clock cost** and byte-identical output. 2 CPUs is cheaper still
  (335 CPU-s) but +69% wall.
  → addressed: `convert_pdfs.py --cpu-limit N` (Windows affinity mask + POSIX `sched_setaffinity`),
  with the measurement table in `limit_cpus()` so it is not re-litigated
- [x] **docling's own thread knobs are inert — do not reach for them** — `AcceleratorOptions(num_threads)`,
  `OMP_NUM_THREADS` and `torch.set_num_interop_threads()` were each verified ineffective (parallelism
  stayed at ~6.1x in all three cases; `OMP_NUM_THREADS` does cap intra-op threads 10 → 4, but the work
  is in the inter-op pool). Only OS affinity binds.
  → addressed: recorded in `limit_cpus()` docstring
- [x] **TableFormer FAST mode must never be used on mark schemes** — 18% cheaper (611 → 503 CPU-s) and
  it **silently drops marking points**. On one MS, two of three marking points vanished from a 3-mark
  part; "award full marks for" appeared 8x under ACCURATE and 5x under FAST; rows duplicated and mark
  columns mis-split. A table-integrity gate does not catch this — pipe counts went *up*.
  → addressed: recorded here; no code change (ACCURATE is already the default, this is a "do not
  optimise here" marker)

### Reproducibility

- [x] **`requirements.txt` pinned nothing that determines output bytes** — `docling>=2.107` floated, so
  two machines could produce different markdown for the same PDF and silently fork a committed corpus.
  Client deps for the remote path (`requests`, `docling-core`) were undeclared entirely; they happened
  to be present on the machine that wrote them.
  → addressed: `docling==2.107.0`, `docling-core==2.85.0`, `requests>=2.31`. The `docling-core` pin is
  load-bearing on the CLIENT: `export_to_markdown()` runs client-side, so the client's version, not
  the server's, decides the bytes
- [ ] **Nothing enforces that server and client pins agree** — `remote_setup_windows.ps1` and
  `requirements.txt` now carry the same three versions in two places, by hand. A mismatch is silent
  and forks the corpus. Candidate: client sends its `docling-core.__version__` on the first request
  and refuses to proceed on disagreement
- [ ] **Any tool writing corpus `.md` must open with `newline="\n"`** — on Windows the default text mode
  emits CRLF, which makes every line of every file differ from a local conversion. Cost this build two
  false "total mismatch" results (once in the remote client, once from git's `autocrlf`). `convert_pdfs.py`
  already does this correctly; the rule is undocumented anywhere a new script author would see it

### Remote offload (docling-serve)

- [x] **docling-serve gives ZERO local CPU saving — do not deploy it for that reason** — it is a FastAPI
  wrapper around the same library loading the same torch models on the same machine: 583 vs 611 CPU-s,
  byte-identical output. It is only worth anything on a *different* box
- [x] **docling-serve does not expose `compact_tables`, which the pipeline depends on** — asking the
  server for markdown roughly doubles table characters and forks the corpus.
  → addressed: `remote_convert.py` requests `json` and runs `export_to_markdown(compact_tables=True)`
  client-side; inference still happens remotely, the export is free
- [x] **The synchronous endpoint has a 120 s ceiling that no client timeout can override** —
  `DOCLING_SERVE_MAX_SYNC_WAIT` defaults to 120 s and returns 504. The original client set an 1800 s
  *client* timeout and passed only because the reference machine was fast enough (35–44 s); on the
  spare box the same PDFs took 135 s and 293 s, so every real conversion would have failed.
  → addressed: client moved to `/v1/convert/file/async` + long-poll `/v1/status/poll/{id}`; launcher
  also raises `DOCLING_SERVE_MAX_SYNC_WAIT` as defence-in-depth
- [x] **Setup script silently reused a stale venv** — it version-checked `python` on PATH but created the
  venv only if absent, so it reported "Python 3.14" while installing into a 3.13 venv. Root cause of two
  failed runs.
  → addressed: guard compares `pyvenv.cfg` against the checked interpreter and aborts before pip
- [ ] **Python version guidance is inverted, and still wrong in the script text** — `docling-jobkit[ray]`
  gates `ray~=2.52` on `python_version < "3.14"` and there is no cp313 Windows wheel, so **3.13 fails
  with `ResolutionImpossible` and 3.14 is the only version that resolves** (the marker drops ray). The
  process docs said the opposite, and `remote_setup_windows.ps1` line 34 still throws
  "Install Python 3.12 or 3.13 first"
- [ ] **Setup script reports success on a no-op firewall rule** — it creates the rule on the Private
  profile without checking the adapter's active profile. On the spare box the WiFi adapter was Public,
  so the rule was correct, enabled and did nothing; cross-machine `/health` failed until the network was
  reclassified. Should read the active profile and either target it or say plainly why it will not work
- [ ] **Offload economics do not generalise — state them before anyone rolls this out** — the spare box
  ran ~9.8 s/page (~10 h for 3,734 pages) against ~2.3 h wall on the laptop, and `--concurrency 2` gave
  no throughput gain while free RAM fell to 0.72 GB (docling already saturates 4 cores, and
  `eng_loc_share_models=False` means each worker loads its own models). With `--cpu-limit 4` the laptop
  finishes 4x sooner *and* leaves 8 logical CPUs free. Offload buys a fully idle machine and overnight
  running — not speed — unless the remote box is genuinely stronger
- [ ] **Conversion is byte-deterministic, so a corpus should be converted once and shared** — verified
  identical across thread counts, affinity settings and an HTTP boundary. For a distributed team this
  beats every hosting option: convert once, share the `.md`, and recipients validate with
  `convert_pdfs.py --verify` without converting anything. Candidate: make the shared corpus the
  documented default and treat local conversion as the exception

### Environment

- [ ] **Windows MAX_PATH headroom is thin on Pearson filenames** — board filenames run to 134 chars; the
  4PH1 corpus tops out at 223-char full paths, ~248 under a typical OneDrive-synced profile, against a
  260 limit. Deeper trees or longer usernames will fail with a bare "No such file or directory" from
  docling on a file that plainly exists (seen once this build). Candidate: converter checks path length
  up front and names the real cause

## PUA normalisation — F97 sweep reaches a second course (2026-08-11, Edexcel GCSE 1PH0)

Triggered by the spare-machine test flagging 7 PUA characters in one converted mark scheme.
The 7 it flagged were harmless; chasing them found a course that had never been swept.

- [x] **`scripts/normalise_pua.py` — the F97 repair, as a reusable script** — the open F97 item asked
  for PUA normalisation in the converter plus a sweep of every other Pearson-PDF course. This is the
  sweep half, parameterised: `<corpus-root> [--dry-run]`, with a verified mapping table, an explicit
  furniture list, an explicit unresolved list, and a loud UNKNOWN bucket for anything unclassified.
  Applied to 1PH0: **271 substitutions across 22 files, 0 unknowns**. Idempotent (re-run reports
  0 substitutable). Still owed: the IAL export's 222 live docs, and folding this into the converter
  so new corpora arrive clean.
  → the mapping is keyed per-codepoint but was VERIFIED per (codepoint, font); the script asserts
  no codepoint is unclassified before writing
- [x] **Map per (codepoint, font), never per codepoint alone** — `U+F053` is a tick in Wingdings2 but
  Σ in Adobe Symbol; `U+F079` is 'y' in a text font but **½** in MSReferenceSpecialty. Deciding from
  the codepoint alone would have written Σ into seven mark schemes. The census that makes this safe is
  a PDF scan grouping by `(ord(char), span["font"])`, not a markdown scan — the markdown has lost the
  font by definition
- [x] **Nine mappings needed a page render, not reasoning** — context inference got most of the way,
  but `U+F079` read as unremarkable (`(KE=) x 0.42 x 12^2`) until rendered, at which point the missing
  **½** in a kinetic-energy calculation was obvious. `U+F04F`/`U+F0FB` proved to be ✗ (not ticks),
  and `U+F0A3` a form checkbox. **Render before trusting a mapping that changes a number or an operator**
- [x] **Do not substitute what the SOURCE cannot render** — one `U+F02D` renders as tofu in the PDF
  itself (absent from the embedded subset), so no engine can recover it and any substitution is a guess.
  It is listed as UNRESOLVED and left in place rather than repaired to something plausible
- [x] **Large-bracket/radical pieces are not substitutable at all** — the Adobe Symbol `U+F8E5`–`U+F8FE`
  range is *construction segments* for tall brackets and radicals (one file carries 51 of them drawing a
  single `sqrt(` ). No single character stands in for a bracket segment; mapping them would misstate the
  expression. Treated as furniture — but their presence marks an expression whose visual structure the
  conversion has flattened, which is a research-time caution, not a repair

### Two findings that outlive this sweep

- [ ] **The damage is invisible to every existing gate** — a PUA character is present, so it is not an
  empty page, not a lost table row, not a legibility failure. `n → p + e` converts to `n  p + e`: the
  table gate passes, the glyph audit counts it, and nothing says the equation stopped being an equation.
  The F20 audit found this on 4PH1 and 1PH0 still carried it 4 days later, on a corpus that had passed
  its conversion gate. Candidate: converter fails, not reports, when a meaning-carrying PUA codepoint
  (the known mapping table) appears outside the furniture set
- [ ] **Corpora differ in line endings by conversion vintage** — 1PH0's markdown is CRLF while 4PH1's is
  LF (`convert_pdfs.py` writes LF explicitly). Anything reconverting a 1PH0 file will flip it and show a
  whole-file diff that looks like total corruption but is pure EOL. Any script touching a corpus in place
  must read AND write with `newline=""` to preserve what is there — `normalise_pua.py` does. Candidate:
  a one-off normalisation of 1PH0 to LF, deliberately, so the vintage difference stops being a trap
