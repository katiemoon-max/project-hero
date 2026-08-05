---
name: hero
description: Status orchestrator for the Project Hero pipeline. Reads project.json in the current project directory (or asks which project), prints lifecycle stage, unit/wave/gate status and the next command. Use to re-orient at any point — especially across sessions or after a handover.
---

# /hero — Project Hero pipeline orchestrator

You are the status orchestrator for a Project Hero course-knowledge build. The lifecycle: **setup → research → write → check → publish** (`/hero-0-setup` → `/hero-1-research` → `/hero-2-write` → `/hero-3-check` → `/hero-4-publish`), producing per-subtopic knowledge files in the Cobalt doc store. (There is no vault stage: the per-SP vault build was an earlier, inferior version of the pipeline, retired 2026-08-05 — research works straight from the stage-0 artifacts and the converted corpus. A `vault` block in project.json now appears only on legacy courses that adopted a pre-existing vault.)

## Steps

1. **Locate the project.** Look for `project.json` in the current working directory, then in any known Project Hero project folder. If several exist, ask which one. If none exists, tell the user to run `/hero-0-setup` first.
2. **Read state.**
   - `project.json` — course identity, lifecycle status, structure ratification, `corpus.conversion.status`, paths (incl. `skills_map` and `cobalt_content`), model policy, research mode, template variant, plus the legacy `vault` block where a pre-existing vault was adopted
   - If in the wave stages: the current wave-state file `research/<unit-key>/_wave<N>-state.md` with the highest unit/wave numbers — **this file carries the rulings and per-subtopic stage grid; it is the working memory, not this skill**
   - `upload-manifest.json` — live document count
3. **Print a compact status block:**
   - Course + Cobalt course id
   - Lifecycle stage: structure ratified? · corpus conversion (pending/running/complete, **and whether the table-integrity gate passed** — `corpus.conversion.table_gate_passed`) · stage-0 evidence artifacts present (`skills-map.json`, Cobalt commentary file — or dated null rulings) · research entry gates passed (skeleton ratified?) · waves · legacy vault adopted (only if present)
   - If in waves: units complete / in progress / remaining (subtopic counts), and the current wave's per-subtopic stages (R1 / R2 / R3 / W / C / F / S / uploaded) from the wave-state grid
   - Open gates: unratified structure or skeleton, incomplete conversion, a conversion whose table-integrity gate has not passed, unapplied pack corrections, pending prompt hardenings, checker reports awaiting fixers, sweeps not yet run, upload HOLDs awaiting the user
   - Any ⚠️ rulings at the top of the wave-state file
4. **Name the next command**: one of `/hero-1-research`, `/hero-2-write`, `/hero-3-check`, `/hero-4-publish` — or the specific unblocking action (e.g. "corpus conversion still running — finish it before `/hero-1-research`", or "apply the pack corrections at the top of the wave-state file before launching wave N+1").

## Hard rules (all earned by defects in production use)

- **Always read the current wave-state file before resuming wave work** — never resume from a handover or this skill alone; a handover's stated counts have been wrong before
- Never launch a new wave while the previous wave's "upstream pack corrections owed" list is non-empty
- `project.json` is the single source of truth for course config and lifecycle state; the wave-state files carry the wave-level rulings
- The pipeline's stage prompts live in the project's `prompts/` directory (R1/R2/R3/WRITER/CHECKER/FIXER) — agents are launched with "Follow ALL instructions in <prompt file>" + parameters, never with inlined rules
