---
name: hero-3-write
description: Stage 3 of the Project Hero pipeline — wave writing. Launches one writer agent per subtopic with the evidence pack, sibling-boundary CAUTIONS and R1 flag rulings. On a course's first wave, opens with a user-ratified pilot of 1–2 subtopics. Requires completed research packs from /hero-2-research.
---

# /hero-3-write — writers

Read `project.json` and the wave-state file. Writer model per project policy (default Opus).

**First wave of a new course: pilot first.** Draft 1–2 subtopics, stop, and get the user's approval of the files before launching the rest of the wave — the approved pilot files become the course's style exemplars (recorded in `project.json` → `exemplars`). Template drift caught at two files costs two files; caught at fifteen it costs the wave.

## Per subtopic

Launch: "Follow ALL instructions in `prompts/WRITER.md`" + parameters — SUBTOPIC (verbatim Cobalt name), SECTION, TOPIC, UNIT, SP_NAMES (Cobalt order, verbatim), RESEARCH_DIR, OUTPUT_FILE, CAUTIONS (that subtopic's sibling-boundary rulings + R1 flag decisions + any pack-specific bans from the wave-state file).

## Orchestrator rules

- Multi-SP subtopics: SP_NAMES order and spelling come from `sp-mapping.json`, never from vault filenames
- Subtopic names containing colons: the YAML `subtopic:` value must be double-quoted (upload breaks otherwise)
- Writers report their own self-check results (certainty audit, direction audit, symbol sweep) — record self-caught items in the wave-state file, but **never trim the checker on the strength of a writer self-check** (ratified negative result from the pilot build: writer-side hardening did not reduce the blocker class reaching the checker)
- Mark W complete in the wave-state grid as each draft lands

Next: `/hero-4-check` per drafted subtopic (no wave-wide barrier).
