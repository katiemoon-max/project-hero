# Project Hero

A course- and subject-agnostic pipeline for building **exam-course knowledge files** with Claude Code: research-grounded, per-subtopic revision/teaching documents built from past papers, mark schemes and examiner reports, quality-gated by adversarial checker agents, and published to the Cobalt CMS document store.

Everything course-specific lives in one config file (`project.json`). The skills, stage prompts and scripts never need editing per course — they have run unchanged across sciences pilots and are designed to work for any board, qualification or subject (sciences, humanities, languages).

## The two stages

1. **Vault build** (`/project-hero`) — interactive, batch-by-batch build of an Obsidian vault with **one note per specification point**: verbatim spec text, examiner-report citations (grounded in NotebookLM sources, never fabricated), exam-appearance evidence and subject-specific skills.
2. **Knowledge-file export** (`/hero-0-setup` → `/hero-4-publish`) — converts a completed vault into per-subtopic knowledge files and uploads them to Cobalt, in waves of ~15 subtopics, with a research → write → check → publish gate structure. `/hero` re-orients you at any point.

## Pipeline (per wave)

```
/hero-1-research   R1 vault digest → R2 verbatim MS/QP extraction → R3 examiner-report
                   cross-check (local sweep by default; NotebookLM variant available)
                   + coverage-gate top-up of R2
/hero-2-write      one writer agent per subtopic, scaffolded by the evidence pack
/hero-3-check      adversarial checker (strongest model tier) → orchestrator rulings
                   (the paper outranks everything) → fixer → fixer-diff sweep →
                   sampled blind re-audit
/hero-4-publish    protect/preflight/strip sweeps → HOLD for human spot-check →
                   sequential createDocument upload → manifest + live retrieval check
```

The design principle throughout: **nothing invented, everything traceable**. Every number, quote and marking claim in a shipped file traces to a verbatim extract from a real paper, and the checker demands the trace. Most of the rules in the prompts were earned by real shipped-or-nearly-shipped defects; each carries its lesson with it.

## Repository layout

| Path | Contents |
|---|---|
| `skills/` | Claude Code skills — copy each folder into `.claude/skills/` (project) or `~/.claude/skills/` (user) |
| `templates/prompts/` | The seven stage prompts (R1, R2, R3-local, R3-nlm, WRITER, CHECKER, FIXER). `/hero-0-setup` copies them into a new project's `prompts/` directory; agents are always launched with "Follow ALL instructions in <prompt file>" + parameters |
| `templates/project.json.template` | The single per-course config: paths, corpus conventions, exam-section skeleton, skills-line label, model policy, quality gates |
| `templates/README-template.md` | Export README skeleton incl. the knowledge-file template rules block |
| `templates/WRITER-SLICE.md` | The pipeline blueprint — model mix rationale, stage design, failure modes |
| `scripts/` | Build/QA scripts: `build_mapping.py` (vault ↔ Cobalt SP mapping), `preflight_sweep.py`, `strip_for_cobalt.py`, `protect_starred_refs.py`, `verify_starred_refs.py`, `fixer_diff_sweep.py` |

## Getting started

1. Copy the `skills/` folders into your Claude Code skills directory.
2. Build (or have) a vault with one note per spec point — `/project-hero` walks you through it.
3. Convert your past-paper corpus to per-sitting markdown files (QP / MS / ER per sitting).
4. Run `/hero-0-setup` — it gathers the course facts, ratifies the exam-section template against real papers (hard gate) and writes `project.json`.
5. Run waves: `/hero-1-research` → `/hero-2-write` → `/hero-3-check` → `/hero-4-publish`. Use `/hero` any time to re-orient.

## Requirements

- **Claude Code** with the Cobalt content MCP (`createDocument` / `updateDocument` / `getCourseStructure` / `searchRevisionNotes` etc.)
- **NotebookLM MCP** — required for the `/project-hero` vault build; optional for the export pipeline (`research_mode: "nlm"` or `"hybrid"`)
- **Python 3.9+** with `commonmark` for the starred-ref scripts: `pip install -r scripts/requirements.txt`
- **git** — the fixer-diff sweep diffs fixer output against the pre-fixer state, so knowledge-file masters should be committed before fixers run

## Key invariants (do not relax)

- `createDocument` has no delete or move — **never create twice**; fixes to live docs go through `updateDocument`
- No upload without an explicit human HOLD approval per wave
- The checker tier is never trimmed and never downgraded below Opus 5
- Orchestrator cautions and EXTRA_CHECKS are directed attention, never deletion orders — when agents disagree, the orchestrator reads the paper; the paper outranks everything
- Wave-state files are the working memory: rulings, stage grids and correction lists live there, not in skills or handovers
