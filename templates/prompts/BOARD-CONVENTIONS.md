# BOARD-CONVENTIONS — per-course marking-conventions extraction (Project Hero)

You will be given parameters: COURSE, SPEC_CODE, SPEC_PATH (the converted specification), CORPUS_DIR, OUTPUT_FILE, HAS_LEVELLED (true/false, from `project.json` → `template.has_levelled_questions`), plus optional NOTES.

Purpose: ONE extraction per course of the board's marking conventions, read by every writer slice (`WRITER.md` input 4) and never re-derived per subtopic. This file exists to stop sibling documents describing one marking mechanism three different ways — which is exactly what happens when each of a wave's writers re-derives the conventions alone (F29).

**Read local files only** — the converted specification, mark schemes and examiner reports under CORPUS_DIR. No MCP calls, no notebook: this extraction must never be blockable by an expired token, and it depends on no wave's research output.

## Where the conventions actually live (earned, F29)

- **The "General Marking Guidance" page printed at the head of every mark scheme is largely a red herring.** It is examiner-facing *procedure* — mark positively, no ceiling on achievement, consult the team leader, crossed-out work rules. Almost none of it changes what a student should write. Skim it once; quote only lines with student-facing consequences.
- **The real conventions live in the marking grids' Additional-guidance column**: `accept` / `allow` / `ignore` / `reject` semantics, `ORA` (or reverse argument), "award full marks for the correct answer without working", priced-error / partial-credit chains, significant-figure acceptance rules, and the bracketed-unit convention. Sweep a spread of mark schemes (multiple sittings, both/all papers) and extract each recurring convention with verbatim examples.
- **Command words: the specification's own taxonomy appendix is the definitional authority.** Most boards print every approved command word with its definition (e.g. Edexcel GCSE spec Appendix 4: Taxonomy, ~29 words). Never infer definitions from usage when the board prints them — the corpus sweep supplies *usage and traps*, not definitions. Cite the appendix by name.
- **Traps need examiner reports.** The "common traps" column can ONLY come from ERs — a sweep scoped to spec + mark schemes produces an empty or invented traps column. Where the ER corpus is thin for a command word, write "no ER evidence" rather than inventing.

## Output (write to OUTPUT_FILE)

1. **Command words** — table: command word | definition (verbatim from the spec appendix, appendix cited) | what to do | common traps (ER-cited, or "no ER evidence")
2. **Marking-grid conventions** — one entry per convention, each with 1–2 verbatim examples cited (file + question ref): accept/allow/ignore/reject semantics, ORA, full-marks-without-working, ecf/priced-error chains, sig-fig rules, unit conventions (incl. bracketed units)
3. **Levelled/extended-response mechanism** — only if HAS_LEVELLED: the board's generic scoring mechanism (levels, descriptors, how indicative content is used), verbatim where possible. This file is the ONE place the generic mechanism lives — knowledge files exclude it by rule, so writers must be able to rely on it here
4. **Caveats** — anything observed but not groundable, and any corpus gaps hit

HARD RULES:
- Quotation marks ONLY around verbatim source text; a convention you cannot cite does not go in the file
- Count claims: per-file `grep -c` only
- Ligature/PUA and page-break gotchas apply as in R2 — a clean grep near a symbol-font glyph proves nothing; read past `## Page N` markers mid-quote

Return: section counts, files read, and any gaps (e.g. command words in the appendix never yet seen in a paper).
