---
name: hero-2-write
description: Stage 2 of the Project Hero pipeline — wave writing. Launches one writer agent per subtopic with the evidence pack, sibling-boundary CAUTIONS and R1 flag rulings. On a course's first wave, opens with a user-ratified pilot of 1–2 subtopics. Requires completed research packs from /hero-1-research.
---

# /hero-2-write — writers

Read `project.json` and the wave-state file. Writer model per project policy (default Opus).

**First wave of a new course: pilot first.** Draft 1–2 subtopics, stop, and get the user's approval of the files before launching the rest of the wave — the approved pilot files become the course's style exemplars (recorded in `project.json` → `exemplars`). Template drift caught at two files costs two files; caught at fifteen it costs the wave.

**Pilot launches use `EXEMPLARS: none — PILOT` (F33)** — a documented value with an instruction behind it in `WRITER.md`, never an empty parameter a writer silently falls through. Pick the pilot pair to **bracket the wave**, not sit in its middle: one multi-SP and one single-SP subtopic, one from each sibling cluster, so the approved exemplars anchor both ends of the range. The pilot writers' return summaries carry their register decisions (length per key concept, worked-example count, choices where the template was silent) — **present those decisions to the user alongside the files**, because approving the pilot is approving them, and an approver shown only the artefact has to reverse-engineer the choices from it.

**Present the pilot unambiguously (earned 2026-08-06).** The approval request LEADS with the exact paths of the drafted files, named as the writer output — never buried as links mid-document. If anything confusable sits within the reviewer's reach — retired vault notes, research packs, batch data (the two generations can share a filename: the pilot course had two different `Acceleration` files) — name it explicitly as NOT the output, or quarantine it first per the `/hero` hard rule. Tell the reviewer where to record feedback (the review note, or back to the orchestrator) — never inside pipeline-owned output directories, which are regenerated. A reviewer opened the retired vault's per-SP notes believing them to be this stage's output and nearly failed the pilot on abandoned files while the real drafts sat behind links.

**Where the two pilot files diverge and both are compliant, that is a prompt gap — surface it, don't bury it.** Present the divergences as a decision table for the user's ruling (the pilot course produced five: worked-example heading attribution, `**Answer:**` line, frontmatter quoting, command-word verbatimness, symbol form in "Where:" lists). Each ruling goes into the project README's template rules and, where it is course-agnostic, back into `prompts/WRITER.md` — the exemplar alone does not stop the next writer diverging on a sixth axis.

## Per subtopic

Launch: "Follow ALL instructions in `prompts/WRITER.md`" + parameters — SUBTOPIC (verbatim Cobalt name), SECTION, TOPIC, UNIT, SP_NAMES, HIGHER_TIER_ONLY, RESEARCH_DIR, OUTPUT_FILE, CAUTIONS (that subtopic's sibling-boundary rulings + R1 flag decisions + any pack-specific bans from the wave-state file).

- **SP_NAMES = the bare `sp_name` values from `sp-mapping.json`, in Cobalt order (F35).** Name the *field*, not just "verbatim" — *verbatim of what* was exactly how two compliant pilot writers produced opposite headings. The spec-point **coordinate never enters the writer's parameters**: `sp_name` and `coord` are separate Cobalt fields, so `2.1.5.1 Acceleration` is a string that exists nowhere in Cobalt, and a coordinate in a heading slot yields unpublishable student-facing prose (`#### How 2.1.5.2 Freefall Appears in Exams`)
- **HIGHER_TIER_ONLY = each SP's tier flag from `sp-mapping.json` (`true | false | "partial"` + note — F56/F50).** There was previously no channel by which a tier fact was *required* of a writer, and the correct answer sat unread in four artifacts while a false "both tiers set it" shipped to a draft. Where the flag is `"partial"`, pass the boundary note — the writer must state which half is which
- **Where a split statement's halves live in different subtopics (F60), say so in CAUTIONS**: a writer drafting `Newton's Third Law` is told it owns the core half of 2.23 and the collision half belongs to `Conservation of Momentum` — derived mechanically from the split map at setup, never recovered by ruling after drafting

## Orchestrator rules

- **`paths.board_conventions` must be a real file before any writer launches (F29/F31).** This stage only *asserts* the path — the producer is the closing act of wave 1's `/hero-1-research`, and if the path is null that step was skipped: stop and send the user back there, naming it. A missing conventions file does not error, it makes every writer re-derive the board's conventions alone, and sibling documents drift into describing one marking mechanism three different ways
- Multi-SP subtopics: SP_NAMES order and spelling come from `sp-mapping.json`, never from legacy vault filenames
- Duplicate-SP groups (`primary_id` + `alias_ids` in `sp-mapping.json` — F15): **one note per group, authored once** against the primary id. Never launch a second writer for an alias id; the single note satisfies every Cobalt id in its group
- Subtopic names containing colons: the YAML `subtopic:` value must be double-quoted (upload breaks otherwise)
- Writers report their own self-check results (certainty audit, direction audit, symbol sweep) — record self-caught items in the wave-state file, but **never trim the checker on the strength of a writer self-check** (ratified negative result from the pilot build: writer-side hardening did not reduce the blocker class reaching the checker)
- Mark W complete in the wave-state grid as each draft lands
- As the wave's drafting closes, write completion back to `project.json` → `status` (stage + any blocker left open) — every stage writes its own completion, or the declared source of truth goes stale (F30)

Next: `/hero-3-check` per drafted subtopic (no wave-wide barrier).
