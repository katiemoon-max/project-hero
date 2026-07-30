---
name: hero-0-setup
description: Stage 0 of the Project Hero pipeline — course onboarding. Fetches and ratifies the Cobalt course structure against the tracker CSV (hard gate), gets the source PDFs on disk, sets up the NotebookLM notebook, kicks off corpus conversion and the Cobalt commentary extraction, and writes project.json as the single source of truth for the whole lifecycle. Run once per course before any other /hero-* skill.
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
3. **Filter non-content rows yourself — do not ask the user to ratify them one by one.** Tracker tabs and Cobalt trees both carry rows that are not content to write against — video placeholders above all (names like "Video of …", "Video: …", "… video"). Classify these automatically: `no_content: true` on the Cobalt side, excluded from the cross-check counts on the tracker side. Present them as a single FYI list inside the ratification summary — "N video rows auto-marked no-content; tell me if any of these is wrong" — so the user confirms them in one glance. The per-item ratification ask is reserved for genuine discrepancies.
4. **Diff the two and present the discrepancy report to the user.** Flag, at minimum:
   - Spec points in Cobalt but not the tracker (after the §2.3 filter) — CMS entries with nothing to write against; needs a user ruling
   - Spec points in the tracker but not Cobalt — content the CMS may be missing; needs a user ruling, not a silent skip
   - Name mismatches (fold curly apostrophes and case before flagging; Cobalt names are authoritative for headings — record genuine differences as aliases)
   - Per-subtopic SP counts on both sides, and subtopic names containing colons (YAML double-quoting rule downstream)
5. **The user ratifies the proposed structure before anything is written.** Record the ratification date, the discrepancy list and the rulings in `project.json` → `structure`. A discrepancy resolved here costs one question; discovered in a wave it costs a rewrite.
6. Generate `sp-mapping.json` mechanically from the ratified tree — subtopics keyed by Cobalt id (name, section, topic, sp_ids) and the mapping array with vault filenames derived from the naming convention (`[S.T.Sub.SP] [SP name].md`). The vault is Cobalt-keyed by construction, so this needs no reconciliation stage later. Carry the `no_content` flags into the mapping so writers and checkers treat those SPs as correctly empty.

## 3. Source PDFs on disk (HARD REQUIREMENT — a NotebookLM notebook alone is not a corpus)

Every research stage greps and quotes **locally converted markdown**: R2 reads the local QP/MS corpus unconditionally in every research mode, and `research_mode: nlm` covers a missing **ER** corpus only. A course whose papers exist only inside a NotebookLM notebook cannot start a single wave — this blocked a real onboarding once, so verify it now, not at `/hero-2-research`.

1. **Inventory what is on disk**: every sitting's question paper and mark scheme as PDFs (or already-converted `.md`), plus examiner reports where the board publishes them. Record the corpus location as `paths.corpus_root`.
2. **If PDFs are missing, walk the user through acquisition before anything else proceeds:**
   - Bulk-download from the exam board's past-paper pages with a Chrome bulk-PDF-extractor extension (works well for Edexcel courses)
   - Where papers are login-gated on the board site (common for recent sittings), the user's teacher-portal login or the SME internal paper store are the fallbacks
   - Pulling text back out of NotebookLM via `source_get_content` is a LAST resort — you get NLM's extraction instead of a controlled conversion, and it needs the user's explicit go-ahead
3. Move on only when the QP/MS inventory is complete for every sitting. Missing ERs are fine (they set the research mode at §5); missing QPs or MSs are not.

## 4. NotebookLM notebook

1. Ask whether a notebook exists for this course; if not, walk the user through creating one in the NLM web UI and uploading sources: all past papers, mark schemes and examiner reports (the PDFs from §3), the specification PDF and the extracted Cobalt content file (§6 — upload it once the extraction finishes).
2. Sources renamed to clear paper-code names (e.g. `1PH0 Paper 1H – 2024 June – Mark Scheme`) — ambiguous names cause fabricated citations downstream.
3. Verify **directly against the notebook**: `mcp__notebooklm__notebook_get` returns the title and full source list, proving it is populated and reachable. Record `corpus.notebook_id` in `project.json`. Note absent/duplicate/variant sources (e.g. "Revised Mark Scheme" replacing "Mark Scheme") → `corpus.known_casualties` as source titles.

## 5. Corpus conversion — kick off now, gate later

The research stages grep and quote **local converted markdown**, never raw PDFs — converted `.md` (and CSV) cost a fraction of the tokens of any other format and make every quote verifiable by construction.

1. **Convert the §3 PDFs with `scripts/convert_pdfs.py`** (PyMuPDF text-layer extractor — resumable via a first-line marker, writes `<name>.md` next to each `<name>.pdf`, flags scan-only pages/docs that need OCR or a PDF-direct fallback). Start QPs and MSs now, as background agents — conversion can run while the vault builds. Convert ERs too where they exist; if the ER corpus is missing or unconverted, set `research_mode: nlm` (that is the only thing `nlm` covers).
2. **Spot-check 2–3 converted files per document type** before trusting the corpus — mojibake, ligature glyphs (ﬁ/ﬃ), dropped symbol-font characters and doubled math-alphanumeric glyphs are known artifact classes. Record what you find in `corpus.known_casualties` and the conversion notes; the research prompts carry the countermeasures.
3. Record in `project.json`: `corpus.kind`, the unit/file naming conventions, sitting variants (e.g. "(A)" resits are separate sittings), and casualties as they surface (file paths for local files, source titles for notebook sources — never cite either kind).
4. Track `corpus.conversion.status` (`pending → running → complete`). **`/hero-2-research` gates on `complete`** — waves must never start against a partial corpus.

## 6. Cobalt commentary extraction — kick off now (never defer silently)

The vault build enriches notes with the CMS's existing per-question commentary — `$c{…}` blue-text Commentary and Examiner Tips & Tricks — extracted into one file grouped by spec point. `/hero-1-vault` Step 3 expects `paths.cobalt_content` to point at that file; a null path silently costs the whole vault that layer, which surprises everyone downstream. So the extraction is a setup-stage job:

1. Kick it off now — as a background agent in this session, or as its own session if this one is heavily loaded (it is a big MCP crawl over every published question in the course):

```
Extract all commentary and Examiner Tips & Tricks from [COURSE] in Cobalt.
Use the sme-content MCP. For every published question and question part, find:
- Commentary — text wrapped in $c{...} sequences (renders as blue text in the
  Cobalt UI). This is in the answer modal of structured questions.
- Examiner Tips & Tricks — text between **Examiner Tips and Tricks** and
  **End of Examiner Tips and Tricks**.
Organise the output as a markdown file grouped by spec point. For each entry,
include the spec point(s) it's tagged to and label it as "Commentary" or
"Examiner Tips and Tricks".
Save the file to the project directory as [SPEC-CODE]-Cobalt-Content.md.
```

2. Record the output path as `paths.cobalt_content` as soon as the file exists, and upload it to the notebook as a source (§4).
3. If there is genuinely nothing to extract (e.g. the course has no published questions yet) or the user explicitly rules it out, record `paths.cobalt_content: null` **with a dated ruling** in `structure.cross_check_findings` — an explicit decision, never a silent deferral.

## 7. Write outputs

- `project.json` — the single source of truth: course facts, ratified structure summary, corpus root + notebook id, corpus conventions + conversion status, `paths.cobalt_content` (§6), research mode, skills label, model policy, lifecycle status (start from `templates/project.json.template`; every `template.*` value stays a placeholder until the `/hero-2-research` entry gate ratifies the exam skeleton)
- `cobalt-structure.json` + `sp-mapping.json` (from §2)
- Project README from `templates/README-template.md`; pipeline blueprint `templates/WRITER-SLICE.md`
- Directory skeleton: `research/`, `knowledge-files/`, `prompts/` (copy the seven stage prompts from `templates/prompts/`), `scripts/` (copy the seven `.py` scripts **and `requirements.txt`** — two scripts import `commonmark`, the converter imports `pymupdf`)

Next: `/hero-1-vault` — or, if a per-SP vault already exists for this course, run `/hero-1-vault` and take its **adopt-existing-vault** path (it verifies the vault instead of building one).
