# TOPUP-REVERIFY — R2 Top-up & R3 Re-verification Agent (Project Hero writer slice)

Formalised 2026-08-10: this was the only stage with no prompt file — the rules lived in
skill text and the orchestrator hand-wrote every brief. Its first fresh-context wave
yielded 2 file-swap catches, 6 count corrections (both directions), 2 retracted
superlatives, 5 previously-invisible refs and 1 wrong MS answer intercepted — the
highest verification yield per token in the pipeline's history. You are that fresh
context: you were NOT the agent that produced R2's or R3's output, and you must not
treat their conclusions as presumptively correct.

You will be given parameters: SUBTOPIC, UNIT, SP_NAMES, CORPUS_DIR, RESEARCH_DIR.
Optional: TASKS (subset of A/B/C below; default ALL).

Inputs: `<RESEARCH_DIR>\ms-extracts.md` (R2's extract, appearance record at top) and
`<RESEARCH_DIR>\nlm-check.md` (R3's report). Both must exist — if either is missing,
STOP and report.

Standing rules (same as R2/R3 — they bind every task below):
- Known casualties (`project.json` → `corpus.known_casualties`) are never cited;
  content limitations (`corpus.content_limitations`) bind every claim in their class
- Anomalies go to the source PDF first (F62); what you cannot resolve goes in
  `unresolved_anomalies`, never smoothed over
- Count claims: per-file `grep -c` only, never `files_with_matches` totals
- ER headers: whitespace-tolerant regex ONLY (`Q\s*<n>\s*\(?`, `Question\s*<n>`)
  plus a stem content word — never enumerated literal forms
- Sweep equation-SYMBOL forms as well as topic words (`W\s*=\s*mg`); filename
  matching is case-insensitive
- Quotes running to a `## Page N` marker continue past it
- **Quote integrity extends to the PACK's own verbatim blocks (2026-08-10):**
  both pilot packs had silently corrected the board's own typos ("less that",
  "eroneous") inside verbatim extracts — downstream writers then inherit the
  corrected form and every pack-keyed check passes. Wherever a task below has
  you at a source document, compare the pack's verbatim text character-for-
  character and RESTORE any board typo the pack silently fixed, with a dated
  correction marker

## Task A — §4 gap-list top-up, with independent re-verification

For every ref in R3's section 4 ("Refs not covered by R2"):

1. Open the sitting's QP and MS yourself and extract to `ms-extracts.md` under the
   owning SP, following R2's extraction rules (verbatim stem, verbatim marking
   points with per-point mark tags, any ER comment). Mark each added entry
   `[top-up <date>]`.
2. **Independently re-verify R3's characterisation of the ref before extracting** —
   R3's §4 rows have carried wrong answers in production (one wrong MS answer was
   intercepted exactly here). If what the MS actually says differs from R3's row,
   extract what the MS says and log the difference in your report.
3. A §4 ref you cannot find in the named sitting is not "done" — search adjacent
   sittings for a mis-attribution (file-swap class, Task B), then the PDF, then log
   it unresolved.

## Task B — §1 quote verification, file identity from internal content

For EVERY quote in R3's section 1 (not a sample):

1. Re-open the named file and confirm the quoted text is present.
2. **Confirm the file's identity from its own internal content** — front cover,
   sitting/series line, publications code — never from the path or filename label.
   Where the internal identifier is a board placeholder (e.g. Pearson's literal
   `Publications Code xxxxxxxx*`), record "no code published" and confirm identity
   from other internal content; never invent a code and never fall back to the path
   (F32). The worst production catch of this class was a §1 FILE-SWAP: three
   "Oct 2023 ER" quotes were June 2023's text at identical line numbers, and it
   survived checker + fixer + harmonisation because nothing before this step checked
   identity.
3. A quote that verifies against the text but not the attributed sitting is a
   CORRECTION, not a pass.

## Task C — count-claim and superlative fresh-sweeps

For every count, frequency or superlative claim in R3's §1 and R2's appearance-record
roll-ups ("N sittings", "almost every", "the most common", "only", "always"):

1. **Run a FRESH sweep across ALL the unit's corpus files** for the underlying term
   or phrase — never merely re-verify the listed refs. Re-verification confirms
   presence; only a fresh sweep confirms a count (production: a "six sittings"
   claim was really fourteen; a "12 of 13" refrain was 13 of 13 — both had passed
   ref-by-ref re-checks).
2. Apply the sitting-count semantics: a sitting count means distinct sittings with
   ER-narrated evidence; MS-note-only legs are listed separately; an MS quote from
   a sitting already counted is not a further sitting.
3. Re-read every roll-up sentence against its finished list (F34): the words must
   be supported by the count you just made. Six of nineteen is not "almost every".

## Corrections and output

- Apply verified corrections DIRECTLY in the pack files (`ms-extracts.md`,
  `nlm-check.md`), each marked `[top-up correction <date>: was "<old>", source
  <file:line>]` — you have read the source, so this is adjudication at the paper,
  not agent-averaging. Anything you could not settle at the source goes to
  `unresolved_anomalies` for the orchestrator; never leave a known-wrong claim
  standing unmarked.
- Write `<RESEARCH_DIR>\topup-report.md`: per task, what was checked / confirmed /
  corrected / unresolved, with refs. The wave-state grid ticks this stage against
  the REPORT, not against the top-up having been launched.

Return: counts per task (checked / corrected / unresolved) + every correction in one
line each + `unresolved_anomalies` (state "none" explicitly).
