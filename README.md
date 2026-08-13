# Project Hero

A course- and subject-agnostic pipeline for building **exam-course knowledge files** with Claude Code: research-grounded, per-subtopic revision/teaching documents built from past papers, mark schemes and examiner reports, quality-gated by adversarial checker agents, and published to the Cobalt CMS document store.

Everything course-specific lives in one config file (`project.json`), created at stage 0 and read by every later stage. The skills, stage prompts and scripts never need editing per course — they have run unchanged across sciences pilots and are designed to work for any board, qualification or subject (sciences, humanities, languages).

## Purpose & source policy (ratified 13 August 2026 — this section is the single home; stage prompts cite it, never restate it)

**Project Hero exists to build a source of truth for each course, grounded in official exam board documents, plus the commentary on our own exam questions as an additional source of teacher/examiner expertise — and nothing else.** That source of truth is then used to produce and review Save My Exams resources with authority and confidence in their quality. The direction only ever flows one way: Project Hero sits *upstream* of everything SME publishes. Any published SME resource fed back in as a source creates a circular loop in which the errors this pipeline exists to eliminate validate themselves — which is why the F148 defect (a revision note named "the content backbone") was a purpose violation, not just a prompt bug.

Every input the pipeline touches falls in one of these classes:

| Class | Examples | Standing |
|---|---|---|
| **Board documents** | Specification, question papers, mark schemes, examiner reports, formula booklet, taxonomy appendices | **Evidence.** The only ground for any factual, marking, frequency or tier claim. The backbone of every knowledge file is `ms-extracts.md` + the examiner-report evidence |
| **SME exam-question commentary** | The `$c{}` commentary blocks extracted at stage 0 | **Attributed expertise.** Folded into tips/strategy, contextualised — but it never overrides board evidence, and any claim it makes about marking still needs a scheme behind it before a file may assert it |
| **Cobalt course metadata** | `getCourseStructure` tree, spec-point names and definitions, tracker CSV | **Structural scaffolding**, ratified by the human at stage 0. Shapes what the files cover; never supplies their content |
| **SME published resources** | Revision notes, exam questions, flashcards, articles — anything on the site | **Never sources.** These are the resources the pipeline exists to produce and audit; using them as input recirculates their errors with our own authority stamped on top. The revision note's sole remaining role is the stage-0 coverage-parity report (below) — it is never passed to a research, writer, checker or fixer agent |
| **Pipeline outputs** | Approved exemplars, other courses' masters | **Register and voice reference only**, never content — each exemplar's header says so |

**The revision-note ruling (13 Aug 2026, supersedes the bounded role F148 left in place):** on RN-bearing courses, stage 0 still fetches each subtopic's revision note via `findRevisionNote`, but solely to produce a human-read **coverage-parity report** — what the RN taught against what the specification allocates — so the course owner can see what the new files replace. No `rn.md` enters a research directory or an agent's evidence pack. Courses without revision notes record the usual dated null ruling (F88).

One numbered pipeline, five stages. `/hero` re-orients you at any point.

```
/hero-0-setup      course onboarding: Cobalt structure fetched and RATIFIED by you
                   (diffed against the tracker CSV where the course has one — the diff
                   catches placeholder SPs, missing content, name drift; a course with
                   no Master Syllabus ratifies from the Cobalt tree alone);
                   paper codes + level designations captured; per-SP skills
                   map read directly from the specification; notebook registered; corpus
                   conversion and Cobalt commentary extraction kicked off; project.json
                   written as the single source of truth
/hero-1-research   entry gates first (conversion complete; exam skeleton ratified
                   against real papers) · then per wave: R1 evidence assembly from the
                   stage-0 artifacts → R2 appearance discovery + verbatim MS/QP
                   extraction → R3 examiner-report cross-check (local sweep by
                   default) + coverage-gate top-up
/hero-2-write      one writer agent per subtopic, scaffolded by the evidence pack;
                   a course's first wave opens with a user-ratified 1–2 file pilot
/hero-3-check      adversarial checker (strongest model tier) → orchestrator rulings
                   (the paper outranks everything) → fixer → fixer-diff sweep →
                   sampled blind re-audit
/hero-4-publish    protect/preflight/strip sweeps → HOLD for human spot-check →
                   sequential createDocument upload → manifest + live retrieval check
```

> **Where did the vault stage go?** Earlier versions built a per-spec-point Obsidian vault between setup and research. It was retired (2026-08-05): of the nine things research extracted from it, seven were either copies of stage-0 artifacts or weaker NotebookLM duplicates of what R2/R3 re-derive authoritatively from the converted corpus — and its appearance tables and ER attributions erred in both directions in production. The two genuinely useful layers (the per-SP skills map, the Cobalt commentary) moved to stage 0. Courses that already have a vault from the old stage can still adopt it — see the note at the top of `/hero-1-research`.

The design principle throughout: **nothing invented, everything traceable**. Every number, quote and marking claim in a shipped file traces to a verbatim extract from a real paper, and the checker demands the trace. Most of the rules in the prompts were earned by real shipped-or-nearly-shipped defects; each carries its lesson with it.

A second principle: **token efficiency by construction**. Research agents grep and quote locally converted markdown (a fraction of the cost of PDFs, verifiable by construction); NotebookLM is queried sparingly and never dumped; writer agents read pre-sliced per-SP evidence packs, never source dumps; prompts are referenced by path, never inlined.

## Repository layout

| Path | Contents |
|---|---|
| `skills/` | Claude Code skills (`hero`, `hero-0-setup` … `hero-4-publish`) — copy each folder into `.claude/skills/` (project) or `~/.claude/skills/` (user) |
| `templates/prompts/` | The nine stage prompts (R1-evidence-assembly, R1-vault-digest for adopted legacy vaults, R2, R3-local, R3-nlm, WRITER, CHECKER, FIXER, BOARD-CONVENTIONS — the once-per-course marking-conventions extraction run as the closing act of wave 1's `/hero-1-research`, F29/F31). `/hero-0-setup` copies them into a new project's `prompts/` directory; agents are always launched with "Follow ALL instructions in <prompt file>" + parameters |
| `templates/project.json.template` | The single per-course config: course facts, ratified structure, corpus + conversion status, exam-section skeleton, model policy, quality gates |
| `templates/README-template.md` | Project README skeleton incl. the knowledge-file template rules block |
| `templates/exemplars/` | Pack reference exemplars (F33): two approved files from finished courses (CIE IGCSE `Freefall`, GCSE register; Edexcel IAL `Force & Acceleration`, A-level register) — the register/depth anchor for a new course's pilot writers, register only, never content; each carries a header saying where its form is outdated |
| `templates/WRITER-SLICE.md` | The pipeline blueprint — model mix rationale, stage design, failure modes |
| `scripts/` | Build/QA scripts: `convert_pdfs.py` (PDF → markdown corpus conversion — docling for QP/MS/ER, pymupdf4llm for specifications, with table-integrity, legibility (F32) and spec-bold (F44) gates, the F20 Unicode artifact audit and the F62 orphan-part check), `merge_cobalt_shards.py` (schema-checked merge of the stage-0 commentary shards with count reconciliation and a `--check` staleness gate — F22/F23/F28), `build_mapping.py` (adopted-vault reconciliation), `spec_coverage_gate.py` (F58/F59/F60 — statement allocation, split-tier, and coverage-in-full checks; production-tested on 1PH0), `convert_qp_second_engine.py` (F61/F64 — pymupdf4llm second reading of question papers into a parallel tree, recovering figure-borne text for absence claims), `preflight_sweep.py`, `strip_for_cobalt.py` (with the F70 untitled-callout default label), `protect_starred_refs.py`, `verify_starred_refs.py`, `fixer_diff_sweep.py`. Every gate script fails loudly when it cannot inspect its input (F63/F69) — `GATE COULD NOT RUN` and a non-zero exit, never a quiet "clean" |

## Getting started

1. **Get the source PDFs on disk first** — every sitting's question paper and mark scheme (plus examiner reports where published). A Chrome bulk-PDF-extractor extension pointed at the board's past-paper pages works well (login-gated papers may need a teacher-portal login or the SME internal store). Stage 0 verifies this inventory and refuses to proceed without it.
2. Copy the `skills/` folders into your Claude Code skills directory.
3. Run `/hero-0-setup` — it fetches and ratifies the course structure, verifies the PDF inventory, captures paper codes and level designations, extracts the per-SP skills map from the specification, sets up the notebook, kicks off corpus conversion (`scripts/convert_pdfs.py`) and the Cobalt commentary extraction, and writes `project.json`.
4. Run waves: `/hero-1-research` → `/hero-2-write` → `/hero-3-check` → `/hero-4-publish`. Use `/hero` any time to re-orient.

The converted QP/MS corpus is a **hard precondition** for the research stage in every research mode (`research_mode: nlm` covers a missing *ER* corpus only; a NotebookLM notebook alone is not a corpus) — which is why stage 0 requires the PDFs on disk, starts the conversion early, and `/hero-1-research` refuses to launch a wave until it is complete.

"Complete" means the **conversion gates passed** — table integrity (F17), legibility (F32) and spec bold (F44) — not just that the run finished. Mark schemes are tables, and the conversion is the only thing the research agents ever see, so `convert_pdfs.py` fails loudly (exit 1) if any mark scheme converted to zero pipe characters, if any file is mostly glyph-index lines, if a specification lost its bold — or if no file matched the mark-scheme name pattern at all, since a gate that checks nothing passes vacuously. Audit a corpus converted elsewhere with `python scripts/convert_pdfs.py <corpus_root> --verify`.

## Requirements

- **Claude Code** with the Cobalt content MCP (`createDocument` / `updateDocument` / `getCourseStructure` / `searchRevisionNotes` etc.)
- **NotebookLM MCP** — optional: only the `"nlm"` and `"hybrid"` research modes query it (`"local"`, the default, works entirely from the converted corpus)
- **Python 3.9+** with `commonmark` (starred-ref scripts), `docling` (QP/MS/ER conversion — a table-aware converter is mandatory, not a preference: mark schemes *are* tables and a text-layer extractor destroys them silently, see F17) and `pymupdf4llm` (specification conversion + the bold gate — docling drops bold, and boards use bold semantically, see F44): `pip install -r scripts/requirements.txt`. First conversion run downloads docling's layout + table models (~500 MB, once per machine) and costs roughly 2–3 s per page on CPU. On PEP 668-managed Pythons (e.g. Homebrew) plain `pip install` is blocked — use a venv, or `pip install --user --break-system-packages -r scripts/requirements.txt`
- **git** — `/hero-0-setup` now runs `git init` and commits the scaffold (F42/F63/F66): the fixer-diff sweep diffs fixer output against the pre-fixer state and *refuses to pass* without a baseline, and the fixer's self-report is only checkable against `git diff`. Commit knowledge-file masters before fixers run

## Key invariants (do not relax)

- The Cobalt structure is ratified at stage 0 **by the user** (cross-checked against the tracker where the course has one) — discrepancies (placeholder SPs, missing content, name drift) get explicit rulings, never silent resolution
- `createDocument` has no delete or move — **never create twice**; fixes to live docs go through `updateDocument`
- No upload without an explicit human HOLD approval per wave
- The checker tier is never trimmed and never downgraded below Opus 5
- Orchestrator cautions and EXTRA_CHECKS are directed attention, never deletion orders — when agents disagree, the orchestrator reads the paper; the paper outranks everything
- `project.json` is the single source of truth for course config and lifecycle state; wave-state files are the working memory for rulings, stage grids and correction lists
