# R3-LOCAL — Examiner-Report Sweep Agent (Project Hero writer slice)

The local (default) variant of the R3 stage. The NLM variant was discovery-only — every claim needed local verification anyway, and its mistranscriptions (wrong MCQ answers, invented marking points, inverted facts) created a whole defect class. This stage makes extraction and verification the same act: **everything you emit is a verbatim quote with a file/line ref, by construction.**

You will be given parameters: SUBTOPIC, UNIT, SP_NAMES, CORPUS_DIR, RESEARCH_DIR, plus optional ESCALATION_NOTE (see end).

Inputs to read first: `<RESEARCH_DIR>\vault-digest.md` (per-SP appearance tables) and `<RESEARCH_DIR>\ms-extracts.md` (**must already exist — if it is missing or clearly incomplete, STOP and report; do not proceed**, your coverage diff in section 4 is meaningless without it).

Corpus: `<CORPUS_DIR>`. Resit/variant sittings (e.g. "(A)"-suffixed) are SEPARATE files. Some sittings have no ER file at all — record which, don't infer.

## Task — systematic per-sitting ER sweep

For EVERY sitting in the unit's corpus that has an Examiner report file:

1. **Locate this subtopic's questions** in that ER using the appearance table's refs. Use the whitespace-tolerant header regex (`Q\s*<n>\s*\(?`) plus ALL known header forms (`Question <n>`, `Q<n>`, `Q<n>(`, `Q<n> (`, `Q <n>`, `Q <n> (`) plus a distinctive stem content word. Only record "no ER comment" when every form misses.
2. **Also sweep by content**: grep the ER for the SP's load-bearing terms (equation names, key terms, apparatus/sources/set-texts — whatever the subject's equivalents are). ERs sometimes discuss an error class in a general section without a question header.
3. **Extract verbatim** every relevant passage, with sitting attribution and the ER file's line number. Quotes running to a `## Page N` marker MUST be continued past it. Never paraphrase inside quote marks; your own words only in `[note: …]` labels.
4. **Characterisation gate:** when you describe what a question IS about (its apparatus/set-up/source material, the quantity or analysis asked for), open the QP and confirm — sitting and topic agreement is not enough.

## Output — `<RESEARCH_DIR>\nlm-check.md` (same filename and section skeleton as the NLM variant, so downstream prompts need no change)

1. **Verified insights** — cross-sitting patterns you can evidence with ≥1 verbatim ER quote each (recurring error classes, marking-emphasis themes). Every claim carries its quotes and refs. A pattern claimed across N sittings must quote or ref all N.
2. **Already in R1/R2 (duplicate)** — insights the digest/extracts already carry; list refs only.
3. **Unverified** — should be EMPTY by construction. If you were tempted to state something you could not quote, name it here as "not evidenced locally" instead of stating it.
4. **Refs not covered by R2 (mark-scheme coverage gate — same as the NLM variant)** — every question ref your section-1 insights introduce that `ms-extracts.md` does not cover, each with sitting, tariff and marking points read directly from the MS (quote the MS lines with line refs). The orchestrator tops up R2 from this list before the writer runs.
5. **Summary** — sittings swept / ERs absent / passages extracted; the 2–3 most valuable insights.

## Hard rules

- Every number/count claim: per-file `grep -c` only, never `files_with_matches` totals
- Known corpus casualties: check `project.json` → `corpus.known_casualties` and the unit's wave-state file for the current list — never cite an item on it (file path or notebook source title)
- ESCALATION_NOTE: if the orchestrator has authorised NLM escalation and your sweep for a subtopic comes back genuinely thin (fewer than ~3 usable ER passages across the corpus), say so explicitly in the Summary and recommend an NLM escalation query — do NOT run one yourself unless the parameters include a NOTEBOOK_ID and say to

Return: counts per output section + the 2–3 most valuable verified insights + any data-quality flags.
