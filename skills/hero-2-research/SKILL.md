---
name: hero-2-research
description: Stage 2 of the Project Hero pipeline — wave research. First run per course passes the entry gates (corpus conversion complete, exam skeleton ratified against real papers). Then per wave: wave-state file, R1 (vault digest), R2 (MS/QP verbatim extraction) and R3 (ER cross-check, local or NLM per project.json), with the R2-before-R3 gate and the coverage-gate top-up. Requires a complete or adopted vault from /hero-1-vault.
---

# /hero-2-research — wave research (R1 → R2 → R3)

Read `project.json` and the pipeline blueprint `WRITER-SLICE.md` in the project directory first. One wave ≈ 15 subtopics (max ~19). Concurrency cap per project.json — queue and feed on completion notifications.

**Preconditions:** `project.json` → `vault.status` is `complete` or `adopted`, and `paths.vault_notes` / `paths.corpus_root` point at real content. R1 and R2 run unconditionally in every research mode — `research_mode` switches R3 only. If either input is missing, STOP and send the user back to the right stage — an empty vault digest makes every downstream gate pass trivially, so running anyway fails silently, not loudly.

## Entry gates — first run per course only (before wave 1)

1. **Corpus conversion complete.** `corpus.conversion.status` must be `complete` and `corpus.known_casualties` current. Waves must never start against a partial corpus — R2's candidate selection and R3's sweep both assume every sitting is greppable.
2. **Template check (hard gate).** Open two recent QPs and MSs from the converted corpus and confirm the paper structure (MCQ section? structured questions? levelled/indicative-content questions?). **Record the ratified skeleton in `project.json` → `template.exam_skeleton`, fill `has_levelled_questions`, and get both ratified by the user before wave 1.** A high-tariff question is not evidence of a levelled question, and a practical paper may have no MCQ section at all — template assumptions imported from a previous course silently corrupt every file in a wave. Every `template.*` value must come from this evidence, never from the worked example in the repo's README-template. If any sitting can only be reached through NotebookLM, the retrieval evidence bar is higher: at least four papers, QP and MS both, front cover quoted verbatim for totals/timing — and **no superlative ("highest tariff", "only", "always") enters the skeleton without paper-level confirmation**.
3. **Exemplars.** Two style exemplars max (approved pilot + one structural match). A brand-new course has none yet — the first wave's pilot subtopics (see `/hero-3-write`) become the exemplars after the user approves them.

## Steps

1. **Create `research/<unit-key>/_wave<N>-state.md`** from the previous wave's structure: model mix line, per-subtopic stage grid (R1|R2|R3|W|C|F|S), SECTION/TOPIC/ids from `sp-mapping.json`, multi-SP SP_NAMES tables, and — before anything launches — confirm the previous wave's "upstream pack corrections owed" list is empty.
2. **Write sibling-boundary CAUTIONS** for every cluster of adjacent subtopics in the wave (who owns which equation/concept/practical; which siblings are already live and must be cross-referred, never re-taught). This is load-bearing — orchestrator cautions have repeatedly been wrong in production, so word every caution as directed attention that invites escalation, NEVER as a deletion order.
3. **Launch R1 per subtopic** (model: per project.json research tier) — "Follow ALL instructions in `prompts/R1-vault-digest.md`" + parameters. Record flag-block rulings (which SPs have no skills line, per the project's no-skills marker) in the wave-state file as they land.
4. **Launch R2 per subtopic** with R1's appearance table. If the course has levelled/extended-response questions, the levelled-question index for the unit (`research/<unit-key>/_levelled-questions.md`) is built once, by the first R2 wave of the unit, then cited.
5. **R3 after that subtopic's R2 completes — hard gate.** R3's coverage gate silently degrades if R2 hasn't finished (its section 4 becomes a superset, not a gap list). Mode per project.json (`local` is the default):
   - `local` — `prompts/R3-local-check.md`: systematic per-sitting ER sweep, verbatim quotes with file/line refs by construction (kills the NLM-mistranscription defect class). Same output filename/skeleton as the NLM variant
   - `hybrid` — local first; NLM escalation only where a subtopic's sweep returns fewer than ~3 usable ER passages
   - `nlm` — `prompts/R3-nlm-check.md` as written (apparatus gate + coverage gate); for courses whose ER corpus is missing or unconverted (QP/MS corpus still required — its gates verify against local files)
6. **Top up R2** from each R3's section-4 gap list before the writer runs. Where R3 and R2/digest disagree, the orchestrator reads the paper — never average agents.
7. Update the wave-state grid as each stage completes. Record every ruling inline — the wave-state file is the working memory.

Next: `/hero-3-write` once a subtopic's pack is complete (drafting may begin per-subtopic; no wave-wide barrier).
