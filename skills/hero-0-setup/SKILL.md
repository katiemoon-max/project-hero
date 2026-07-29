---
name: hero-0-setup
description: Initialise a Project Hero knowledge-file export for a new course (any board/subject). Gathers Cobalt course id and structure, corpus and vault-note paths, research mode, exam-skeleton template and exemplars; writes project.json, sp-mapping.json and the export README. Run once per course before any other /hero-* skill.
---

# /hero-0-setup — course onboarding (subject-agnostic)

Initialise a knowledge-file export project. Everything course-specific is captured HERE, in `project.json` — the downstream stage prompts are subject-agnostic and must not need editing per course.

## 0. Preconditions (hard gate — check FIRST, refuse early)

The export pipeline has two unconditional inputs. `research_mode` switches **R3 only** — R1 and R2 run in every mode. Verify both inputs exist before gathering anything else; if either is missing, STOP with the message below. Do not let setup complete and wave 1 fail silently — an empty vault digest passes every downstream gate trivially, so the failure would be invisible.

1. **A per-spec-point vault** (one note per spec point). R1 reads it unconditionally; the digest it produces is the spine of every later stage (R2 candidate selection, R3 coverage gates, writer evidence, checker parity). There is no degraded no-vault mode. **No vault → stop:** "This course has no per-SP vault yet — build one first with `/project-hero`, then re-run `/hero-0-setup`."
2. **A converted local QP/MS corpus** (`.md` per sitting). R2 reads it unconditionally in ALL research modes, and even `nlm` mode's verification and apparatus gates verify claims against local files. `nlm` covers a missing **ER** corpus only — not a missing corpus. **No QP/MS corpus → stop:** "This course's papers are not converted to local markdown — convert QPs and MSs per sitting first (missing ERs can be covered by `research_mode: nlm`), then re-run `/hero-0-setup`."

A NotebookLM notebook, however complete, satisfies **neither** precondition — there is currently no notebook-only research path (no NLM variant of R1 or R2 exists).

## 1. Gather (ask; verify everything the user asserts)

| Item | How to verify |
|---|---|
| Board, qualification, subject, course name | user |
| Cobalt course id (`crs_…`) | `getCourseStructure` — confirm section/topic/subtopic tree loads |
| Vault spec-note directory (one note per spec point) | list it; spot-open two notes and **profile each against R1's nine extraction items** (spec text · exam-appearance table · ER insights with sitting attribution · MS conventions · subject skills or the no-skills marker · practical links · misconceptions · Cobalt commentary · notebook id in frontmatter); record which items are present and which are absent. Absent items are declared research debt for wave 1, not an automatic fail — but a directory of spec-text-only notes satisfies 1 of 9 and starves R1, and this profile is what catches that. Also record the frontmatter schema |
| Research mode: `local` (systematic ER sweep of the corpus — default) / `hybrid` (local + NLM escalation) / `nlm` (ER corpus missing or unconverted; **converted QP/MS corpus still required — see §0**) | user choice, sanity-checked against what the corpus actually contains |
| Past-paper corpus directory (converted `.md` per sitting: QP / MS, plus ER unless mode is `nlm`) | list it; record `corpus.kind` and the file-naming convention in project.json; note missing ERs, sitting variants (e.g. "(A)" resits), unusable items → `corpus.known_casualties` (file paths for local files; source titles for notebook sources — missing, duplicate or variant sources such as "Revised Mark Scheme" replacing "Mark Scheme") |
| If hybrid/nlm: NotebookLM notebook id → `corpus.notebook_id` | verify **directly against the notebook**: `mcp__notebooklm__notebook_get` returns the title and full source list, proving it is populated and reachable. Vault-note frontmatter is a cross-check only, not the source of truth — notebook and vault are independent artefacts |
| Board conventions file (marking guidance, command words, levelled/extended-response mechanism if the course has one) | exists, or schedule its extraction as a first-wave task |
| Skills flag line for this subject (`template.skills_line_label`) | e.g. "Mathematical skills" for sciences/maths, "Source-analysis skills" for history, "Practical skills" for PE — plus the vault notes' no-skills marker phrase (`template.no_skills_marker`) |
| Style exemplars (2 max: approved pilot + one structural match) | files exist |
| Model policy | default: Sonnet research/fixers/upload · Opus writers · checker = strongest available (never below Opus 5); record any override |

## 2. Build `sp-mapping.json`

From `getCourseStructure` + the vault notes (use `scripts/build_mapping.py` as the starting point): subtopics keyed by Cobalt id (name, section, topic, sp_ids) and a mapping array (vault_file ↔ cobalt_sp_id/sp_name/subtopic). Flag: multi-SP subtopics (SP_NAMES order matters), name mismatches between vault and Cobalt (Cobalt names are authoritative for headings — record genuine differences as aliases), subtopic names containing colons (YAML double-quoting rule), and **spec points with no writable content** (e.g. video-placeholder SPs that exist in Cobalt with a heading and nothing to write against) — mark these `"no_content": true` in the mapping so writers and checkers treat them as correctly empty rather than reporting spurious defects.

## 3. Template check (hard gate)

Open two recent QPs and MSs and confirm the paper structure matches the assumed exam-section skeleton (MCQ section? structured questions? levelled/indicative-content questions?). **Record the ratified skeleton in `project.json` → `template.exam_skeleton` and get it ratified by the user before wave 1** — a high-tariff question is not evidence of a levelled question, and a practical paper may have no MCQ section at all. This gate exists because template assumptions imported from a previous course silently corrupt every file in a wave.

Every `template.*` value in `project.json.template` is a placeholder — fill all of them (including `has_levelled_questions`) from this gate's evidence, never from a previous course or from the worked example in `templates/README-template.md`.

**If some sittings are reachable only through NotebookLM** (rare, given §0 — but possible for the specific recent sittings you want): the evidence bar for a retrieval-derived skeleton is higher. Query at least **four papers** (two sittings × two papers where the course has multiple), QP **and** MS for each, and quote the front cover verbatim for totals, timing and tiering. And a hard rule: **no superlative ("highest tariff", "only", "always") may enter the skeleton without paper-level confirmation** — retrieval sees the parts it retrieved, not every part, so a retrieved "highest" is not a highest. Prefer opening local papers wherever they exist.

## 4. Write outputs

- `project.json` — all of the above (paths absolute, ids verbatim; start from `templates/project.json.template` in this repo; every `template.*` placeholder filled from §3 evidence)
- Export `README.md` — template rules block + status checklist (start from `templates/README-template.md`, adjusting the course facts and the exam-skeleton block)
- Pipeline blueprint: copy `templates/WRITER-SLICE.md` into the project directory
- Directory skeleton: `research/`, `knowledge-files/`, `prompts/` (copy the seven stage prompts from `templates/prompts/` — they are subject-agnostic), `scripts/` (copy `strip_for_cobalt.py`, `protect_starred_refs.py`, `verify_starred_refs.py`, `preflight_sweep.py`, `fixer_diff_sweep.py`, `build_mapping.py` **and `requirements.txt`** — two of the scripts import `commonmark`)

Next: `/hero-1-research` for wave 1.
