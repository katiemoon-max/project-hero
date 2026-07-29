# Project Hero

A course- and subject-agnostic pipeline for building **exam-course knowledge files** with Claude Code: research-grounded, per-subtopic revision/teaching documents built from past papers, mark schemes and examiner reports, quality-gated by adversarial checker agents, and published to the Cobalt CMS document store.

Everything course-specific lives in one config file (`project.json`), created at stage 0 and read by every later stage. The skills, stage prompts and scripts never need editing per course — they have run unchanged across sciences pilots and are designed to work for any board, qualification or subject (sciences, humanities, languages).

## The lifecycle

One numbered pipeline, six stages. `/hero` re-orients you at any point.

```
/hero-0-setup      course onboarding: Cobalt structure fetched and RATIFIED against the
                   tracker CSV (hard gate — catches placeholder SPs, missing content,
                   name drift); notebook registered; corpus conversion kicked off;
                   project.json written as the single source of truth
/hero-1-vault      interactive batch build of the Obsidian vault — one note per Cobalt
                   spec point, NotebookLM-grounded, per-batch user confirmation and a
                   5-claim anti-fabrication spot-check (or: adopt an existing vault,
                   verified against R1's nine extraction items)
/hero-2-research   entry gates first (conversion complete; exam skeleton ratified
                   against real papers) · then per wave: R1 vault digest → R2 verbatim
                   MS/QP extraction → R3 examiner-report cross-check (local sweep by
                   default) + coverage-gate top-up
/hero-3-write      one writer agent per subtopic, scaffolded by the evidence pack;
                   a course's first wave opens with a user-ratified 1–2 file pilot
/hero-4-check      adversarial checker (strongest model tier) → orchestrator rulings
                   (the paper outranks everything) → fixer → fixer-diff sweep →
                   sampled blind re-audit
/hero-5-publish    protect/preflight/strip sweeps → HOLD for human spot-check →
                   sequential createDocument upload → manifest + live retrieval check
```

The design principle throughout: **nothing invented, everything traceable**. Every number, quote and marking claim in a shipped file traces to a verbatim extract from a real paper, and the checker demands the trace. Most of the rules in the prompts were earned by real shipped-or-nearly-shipped defects; each carries its lesson with it.

A second principle: **token efficiency by construction**. Research agents grep and quote locally converted markdown (a fraction of the cost of PDFs, verifiable by construction); NotebookLM is queried sparingly and never dumped; writer agents read pre-sliced per-SP evidence packs, never source dumps; prompts are referenced by path, never inlined.

## Repository layout

| Path | Contents |
|---|---|
| `skills/` | Claude Code skills (`hero`, `hero-0-setup` … `hero-5-publish`) — copy each folder into `.claude/skills/` (project) or `~/.claude/skills/` (user) |
| `templates/prompts/` | The seven stage prompts (R1, R2, R3-local, R3-nlm, WRITER, CHECKER, FIXER). `/hero-0-setup` copies them into a new project's `prompts/` directory; agents are always launched with "Follow ALL instructions in <prompt file>" + parameters |
| `templates/project.json.template` | The single per-course config: course facts, ratified structure, corpus + conversion status, vault state, exam-section skeleton, model policy, quality gates |
| `templates/README-template.md` | Project README skeleton incl. the knowledge-file template rules block |
| `templates/WRITER-SLICE.md` | The pipeline blueprint — model mix rationale, stage design, failure modes |
| `scripts/` | Build/QA scripts: `build_mapping.py` (adopted-vault reconciliation), `preflight_sweep.py`, `strip_for_cobalt.py`, `protect_starred_refs.py`, `verify_starred_refs.py`, `fixer_diff_sweep.py` |

## Getting started

1. Copy the `skills/` folders into your Claude Code skills directory.
2. Run `/hero-0-setup` — it fetches and ratifies the course structure, sets up the notebook, kicks off corpus conversion and writes `project.json`.
3. Run `/hero-1-vault` to build the vault batch by batch (or adopt an existing per-SP vault via its verification path).
4. Run waves: `/hero-2-research` → `/hero-3-write` → `/hero-4-check` → `/hero-5-publish`. Use `/hero` any time to re-orient.

The converted QP/MS corpus is a **hard precondition** for the research stage in every research mode (`research_mode: nlm` covers a missing *ER* corpus only; a NotebookLM notebook alone is not a corpus) — which is why stage 0 starts the conversion early and `/hero-2-research` refuses to launch a wave until it is complete.

## Requirements

- **Claude Code** with the Cobalt content MCP (`createDocument` / `updateDocument` / `getCourseStructure` / `searchRevisionNotes` etc.)
- **NotebookLM MCP** — required for the `/hero-1-vault` build; optional for the wave stages (`research_mode: "nlm"` or `"hybrid"`)
- **Python 3.9+** with `commonmark` for the starred-ref scripts: `pip install -r scripts/requirements.txt`. On PEP 668-managed Pythons (e.g. Homebrew) plain `pip install` is blocked — use a venv, or `pip install --user --break-system-packages -r scripts/requirements.txt`
- **git** — the fixer-diff sweep diffs fixer output against the pre-fixer state, so knowledge-file masters should be committed before fixers run

## Key invariants (do not relax)

- The Cobalt structure is ratified against the tracker at stage 0 **by the user** — discrepancies (placeholder SPs, missing content, name drift) get explicit rulings, never silent resolution
- `createDocument` has no delete or move — **never create twice**; fixes to live docs go through `updateDocument`
- No upload without an explicit human HOLD approval per wave
- The checker tier is never trimmed and never downgraded below Opus 5
- Orchestrator cautions and EXTRA_CHECKS are directed attention, never deletion orders — when agents disagree, the orchestrator reads the paper; the paper outranks everything
- `project.json` is the single source of truth for course config and lifecycle state; wave-state files are the working memory for rulings, stage grids and correction lists
