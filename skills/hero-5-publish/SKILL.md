---
name: hero-5-publish
description: Stage 5 of the Project Hero pipeline — wave publish. Runs protect/strip/preflight sweeps, holds for the user's spot-check, then uploads via createDocument and updates the manifest. Upload is irreversible — no delete API — so every gate is mandatory.
---

# /hero-5-publish — sweep, hold, upload

Read `project.json` and the wave-state file. Upload agent: research tier (default Sonnet). **`createDocument` has no delete or move — never create twice; fixes to live docs go through `updateDocument`.**

**Duplicate-SP groups** (`primary_id` + `alias_ids` in `sp-mapping.json` — F15): one note serves the whole group, but **every Cobalt id in the group still exists and still needs publishing** — the upload must satisfy the primary AND every alias id, and manifest/parity counts are per group, never per primary alone.

## Gates (in order, all mandatory)

1. `scripts/protect_starred_refs.py` on the wave's masters (bold Example labels so bare `Q*` refs cannot break emphasis; refs stay UNESCAPED — `Q*16`, never `Q\*16`)
2. `scripts/preflight_sweep.py` on the masters — fix every FAIL (U+1D400 chars, escaped refs, \Delta, $c{, images, links, flag-block parity); review every Oxford-comma candidate
3. `scripts/strip_for_cobalt.py` → `.cobalt.md`, then `preflight_sweep.py --cobalt` (adds callout/blockquote checks)
4. Validate the skills-line total (the `template.skills_line_label` count) against the wave's OWN skills-omission ruling list in the wave-state file — **derive expectations from the wave's files, never from a handover**
5. **HOLD — the user spot-checks a sample.** No upload without explicit approval this wave.
6. Upload sequentially via `createDocument` (`.cobalt.md` content only); append every `document_id` + chunk count to `upload-manifest.json` and the wave-state table; zero-warning uploads are the norm — investigate any warning before continuing
7. Spot-check retrieval live (`queryDocuments` against a couple of the new subtopics)

Close the wave: record final counts in the wave-state file, list any "upstream pack corrections owed" and "prompt hardenings for next wave" at the top — the next wave's `/hero-2-research` gates on that list being applied.
