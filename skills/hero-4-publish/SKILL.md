---
name: hero-4-publish
description: Stage 4 of the Project Hero pipeline — wave publish. Runs protect/strip/preflight sweeps, holds for the user's spot-check, then uploads via createDocument and updates the manifest. Upload is irreversible — no delete API — so every gate is mandatory.
---

# /hero-4-publish — sweep, hold, upload

Read `project.json` and the wave-state file. Upload agent: research tier (default Sonnet). **`createDocument` has no delete or move — never create twice; fixes to live docs go through `updateDocument`.**

**Duplicate-SP groups** (`primary_id` + `alias_ids` in `sp-mapping.json` — F15): one note serves the whole group, but **every Cobalt id in the group still exists and still needs publishing** — the upload must satisfy the primary AND every alias id, and manifest/parity counts are per group, never per primary alone.

## Gates (in order, all mandatory)

1. `scripts/protect_starred_refs.py` on the wave's masters (bold Example labels so bare `Q*` refs cannot break emphasis; refs stay UNESCAPED — `Q*16`, never `Q\*16`)
2. `scripts/preflight_sweep.py` on the masters — fix every FAIL (U+1D400 chars, escaped refs, \Delta, $c{, images, links, flag-block parity); review every Oxford-comma candidate
3. `scripts/strip_for_cobalt.py` → `.cobalt.md`, then `preflight_sweep.py --cobalt` (adds callout/blockquote checks)
4. Validate the skills-line total (the `template.skills_line_label` count) against the wave's OWN skills-omission ruling list in the wave-state file — **derive expectations from the wave's files, never from a handover**
5. **Spec-coverage gate (F60 — BLOCKING).** No wave ships while a spec statement allocated to one of its subtopics is quoted nowhere. Coverage is the **union over every file quoting the statement** — statements are legitimately spliced and merged across subtopics (1PH0's 2.23 lives half in `Newton's Third Law`, half in `Conservation of Momentum`), so a per-file check both false-fails the splits and misses a statement written nowhere. Two checks: **(C) coverage in full** — every content word of the statement's authoritative text appears in the union of its quotes; **(D) wave completeness** — no statement allocated to an already-written subtopic is unquoted (a statement no writer was ever launched for is invisible to every other gate, because nothing else holds the denominator). Implementation: `scripts/spec_coverage_gate.py` (from the 1PH0 build) where present, by hand where not — and the parser must handle **multi-statement quote blocks** (further statements on bare continuation lines below the `> **Specification:**` header; a header-only parse reports written statements as unwritten and sends a writer to duplicate existing work). Print `PASS` explicitly on an empty gap list — never nothing
6. **Content-limitations gate (F65 — BLOCKING).** A non-empty `corpus.content_limitations` with no corresponding mitigation recorded in the wave-state file blocks publish. A limitation with no enforcement point is a note, not a control — 1PH0's figure-text loss was recorded at stage 0, in writing, with the correct remedy attached, and shipped a defect anyway because nothing read the field
7. **HOLD — the user spot-checks a sample.** No upload without explicit approval this wave.
8. Upload sequentially via `createDocument` (`.cobalt.md` content only); append every `document_id` + chunk count to `upload-manifest.json` and the wave-state table, **and mark `S` in the wave-state grid per subtopic as each upload lands (F52 — the grid's columns each need a named owner, and this stage owns `S`)**; zero-warning uploads are the norm — investigate any warning before continuing
9. Spot-check retrieval live (`queryDocuments` against a couple of the new subtopics)

Close the wave: record final counts in the wave-state file, list any "upstream pack corrections owed" and "prompt hardenings for next wave" at the top — the next wave's `/hero-1-research` gates on that list being applied. Then **write `project.json` → `status`** — `stage`, `units_complete`, `docs_live` (from the manifest), `next_unit`, and every blocker knowingly left open (F30: an empty `blockers` array on a project with a live blocker reads as a checked negative). Also apply the wave-close heuristic: an artifact that is *uniformly* missing across the wave is orchestrator-owed — no agent report can surface it (F29).
