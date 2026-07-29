---
name: hero-0-setup
description: Stage 0 of the Project Hero pipeline — course onboarding. Fetches and ratifies the Cobalt course structure against the tracker CSV (hard gate), sets up the NotebookLM notebook, kicks off corpus conversion, and writes project.json as the single source of truth for the whole lifecycle. Run once per course before any other /hero-* skill.
---

# /hero-0-setup — course onboarding (stage 0)

First stage of the Project Hero lifecycle: **setup → vault → research → write → check → publish** (`/hero-0-setup` → `/hero-1-vault` → `/hero-2-research` → `/hero-3-write` → `/hero-4-check` → `/hero-5-publish`, with `/hero` re-orienting at any point).

Everything course-specific is captured HERE, in `project.json` — the single source of truth for every later stage, including the vault build. The downstream stage prompts are subject-agnostic and must not need editing per course.

## 1. Course facts (ask; verify everything the user asserts)

| Item | How to verify |
|---|---|
| Board, qualification, subject, spec code, course name | user |
| Cobalt course id (`crs_…`) | `getCourseStructure` — confirm the section/topic/subtopic/spec-point tree loads |
| Model policy | default: Sonnet research/fixers/upload · Opus writers · checker = strongest available (never below Opus 5); record any override |
| Skills flag line for this subject (`template.skills_line_label`) | e.g. "Mathematical skills" for sciences/maths, "Source-analysis skills" for history, "Practical skills" for PE — plus the no-skills marker phrase (`template.no_skills_marker`) the vault notes will use |

## 2. Structure snapshot + CSV cross-check (HARD GATE — do not skip)

The Cobalt structure is the skeleton for everything downstream — the vault is built one note per Cobalt spec point, so getting this right up front is what kills the vault↔CMS mapping problem. But **Cobalt is not ratified blind**: the tracker cross-check is what catches structure that should not be written against.

1. Save the full `getCourseStructure` tree to `cobalt-structure.json` (sections → topics → subtopics → spec points, all ids and names verbatim).
2. Get the course's Master Syllabus from the subject tracker as a cross-check. **Prefer a downloaded CSV** (most token-efficient — ask the user to File > Download > CSV from the tracker's Master Syllabus tab); fall back to the Google Sheet via URL or Drive MCP if a download is awkward.
3. **Diff the two and present the discrepancy report to the user.** Flag, at minimum:
   - Spec points in Cobalt but not the tracker — classic case: video-placeholder SPs ("Video of …") that exist as CMS entries with nothing to write against → propose `no_content: true` for each
   - Spec points in the tracker but not Cobalt — content the CMS may be missing; needs a user ruling, not a silent skip
   - Name mismatches (fold curly apostrophes and case before flagging; Cobalt names are authoritative for headings — record genuine differences as aliases)
   - Per-subtopic SP counts on both sides, and subtopic names containing colons (YAML double-quoting rule downstream)
4. **The user ratifies the proposed structure before anything is written.** Record the ratification date, the discrepancy list and the rulings in `project.json` → `structure`. A discrepancy resolved here costs one question; discovered in a wave it costs a rewrite.
5. Generate `sp-mapping.json` mechanically from the ratified tree — subtopics keyed by Cobalt id (name, section, topic, sp_ids) and the mapping array with vault filenames derived from the naming convention (`[S.T.Sub.SP] [SP name].md`). The vault is Cobalt-keyed by construction, so this needs no reconciliation stage later. Carry the `no_content` flags into the mapping so writers and checkers treat those SPs as correctly empty.

## 3. NotebookLM notebook

1. Ask whether a notebook exists for this course; if not, walk the user through creating one in the NLM web UI and uploading sources: all past papers, mark schemes, examiner reports, the specification PDF and the extracted Cobalt content file (give the extraction prompt from `/hero-1-vault` if not yet done).
2. Sources renamed to clear paper-code names (e.g. `1PH0 Paper 1H – 2024 June – Mark Scheme`) — ambiguous names cause fabricated citations downstream.
3. Verify **directly against the notebook**: `mcp__notebooklm__notebook_get` returns the title and full source list, proving it is populated and reachable. Record `corpus.notebook_id` in `project.json`. Note absent/duplicate/variant sources (e.g. "Revised Mark Scheme" replacing "Mark Scheme") → `corpus.known_casualties` as source titles.

## 4. Corpus conversion — kick off now, gate later

The research stages grep and quote **local converted markdown**, never raw PDFs — converted `.md` (and CSV) cost a fraction of the tokens of any other format and make every quote verifiable by construction. `research_mode` switches R3 only; R2 reads the local QP/MS corpus unconditionally in every mode.

1. Locate the source PDFs (already in hand from §3) and **start converting QPs and MSs to one `.md` per sitting now**, as background agents — conversion can run while the vault builds. Convert ERs too where they exist; if the ER corpus is missing or unconverted, set `research_mode: nlm` (that is the only thing `nlm` covers).
2. Record in `project.json`: `corpus.kind`, the unit/file naming conventions, sitting variants (e.g. "(A)" resits are separate sittings), and casualties as they surface (file paths for local files, source titles for notebook sources — never cite either kind).
3. Track `corpus.conversion.status` (`pending → running → complete`). **`/hero-2-research` gates on `complete`** — waves must never start against a partial corpus.

## 5. Write outputs

- `project.json` — the single source of truth: course facts, ratified structure summary, notebook id, corpus conventions + conversion status, research mode, skills label, model policy, lifecycle status (start from `templates/project.json.template`; every `template.*` value stays a placeholder until the `/hero-2-research` entry gate ratifies the exam skeleton)
- `cobalt-structure.json` + `sp-mapping.json` (from §2)
- Project README from `templates/README-template.md`; pipeline blueprint `templates/WRITER-SLICE.md`
- Directory skeleton: `research/`, `knowledge-files/`, `prompts/` (copy the seven stage prompts from `templates/prompts/`), `scripts/` (copy the six `.py` scripts **and `requirements.txt`** — two scripts import `commonmark`)

Next: `/hero-1-vault` — or, if a per-SP vault already exists for this course, run `/hero-1-vault` and take its **adopt-existing-vault** path (it verifies the vault instead of building one).
