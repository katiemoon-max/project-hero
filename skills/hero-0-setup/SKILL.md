---
name: hero-0-setup
description: Initialise a Project Hero knowledge-file export for a new course (any board/subject). Gathers Cobalt course id and structure, corpus and vault-note paths, research mode, exam-skeleton template and exemplars; writes project.json, sp-mapping.json and the export README. Run once per course before any other /hero-* skill.
---

# /hero-0-setup — course onboarding (subject-agnostic)

Initialise a knowledge-file export project. Everything course-specific is captured HERE, in `project.json` — the downstream stage prompts are subject-agnostic and must not need editing per course.

## 1. Gather (ask; verify everything the user asserts)

| Item | How to verify |
|---|---|
| Board, qualification, subject, course name | user |
| Cobalt course id (`crs_…`) | `getCourseStructure` — confirm section/topic/subtopic tree loads |
| Vault spec-note directory (one note per spec point) | list it; spot-open two notes; record frontmatter schema (number, spec_text, notebook, unit) |
| Past-paper corpus directory (converted `.md` per sitting: QP / MS / ER) | list it; record the file-naming convention in project.json; note missing ERs, sitting variants (e.g. "(A)" resits), known-mojibake files → `corpus.known_casualties` |
| Board conventions file (marking guidance, command words, levelled/extended-response mechanism if the course has one) | exists, or schedule its extraction as a first-wave task |
| Research mode: `local` (systematic ER sweep of the corpus — default) / `hybrid` (local + NLM escalation) / `nlm` (for courses without a converted ER corpus) | if hybrid/nlm: notebook id(s) from vault-note frontmatter, verified against two notes |
| Skills flag line for this subject (`template.skills_line_label`) | e.g. "Mathematical skills" for sciences/maths, "Source-analysis skills" for history, "Practical skills" for PE — plus the vault notes' no-skills marker phrase (`template.no_skills_marker`) |
| Style exemplars (2 max: approved pilot + one structural match) | files exist |
| Model policy | default: Sonnet research/fixers/upload · Opus writers · checker = strongest available (never below Opus 5); record any override |

## 2. Build `sp-mapping.json`

From `getCourseStructure` + the vault notes (use `scripts/build_mapping.py` as the starting point): subtopics keyed by Cobalt id (name, section, topic, sp_ids) and a mapping array (vault_file ↔ cobalt_sp_id/sp_name/subtopic). Flag: multi-SP subtopics (SP_NAMES order matters), name mismatches between vault and Cobalt (Cobalt names are authoritative for headings — record genuine differences as aliases), subtopic names containing colons (YAML double-quoting rule).

## 3. Template check (hard gate)

Open two recent QPs and MSs and confirm the paper structure matches the assumed exam-section skeleton (MCQ section? structured questions? levelled/indicative-content questions?). **Record the ratified skeleton in `project.json` → `template.exam_skeleton` and get it ratified by the user before wave 1** — a high-tariff question is not evidence of a levelled question, and a practical paper may have no MCQ section at all. This gate exists because template assumptions imported from a previous course silently corrupt every file in a wave.

## 4. Write outputs

- `project.json` — all of the above (paths absolute, ids verbatim; start from `templates/project.json.template` in this repo)
- Export `README.md` — template rules block + status checklist (start from `templates/README-template.md`, adjusting the course facts and the exam-skeleton block)
- Pipeline blueprint: copy `templates/WRITER-SLICE.md` into the project directory
- Directory skeleton: `research/`, `knowledge-files/`, `prompts/` (copy the seven stage prompts from `templates/prompts/` — they are subject-agnostic), `scripts/` (copy `strip_for_cobalt.py`, `protect_starred_refs.py`, `verify_starred_refs.py`, `preflight_sweep.py`, `fixer_diff_sweep.py`, `build_mapping.py`)

Next: `/hero-1-research` for wave 1.
