---
name: hero
description: Status orchestrator for the Project Hero knowledge-file pipeline. Reads project.json in the current export directory (or asks which project), prints unit/wave/gate status and the next command. Use to re-orient at any point — especially across sessions or after a handover.
---

# /hero — Project Hero pipeline orchestrator

You are the status orchestrator for a Project Hero course-knowledge export (vault → per-subtopic knowledge files → Cobalt doc store).

## Steps

1. **Locate the project.** Look for `project.json` in the current working directory, then in any known Project Hero export folder. If several exist, ask which one. If none exists, tell the user to run `/hero-0-setup` first.
2. **Read state.**
   - `project.json` — course identity, paths, model policy, research mode, template variant
   - The current wave-state file: `research/<unit-key>/_wave<N>-state.md` with the highest unit/wave numbers — **this file carries the rulings and per-subtopic stage grid; it is the working memory, not this skill**
   - `upload-manifest.json` — live document count
3. **Print a compact status block:**
   - Course + Cobalt course id
   - Units complete / in progress / remaining (subtopic counts)
   - Current wave: subtopics at each stage (R1 / R2 / R3 / W / C / F / S / uploaded) from the wave-state grid
   - Open gates: unapplied pack corrections, pending prompt hardenings, checker reports awaiting fixers, sweeps not yet run, upload HOLDs awaiting the user
   - Any ⚠️ rulings at the top of the wave-state file
4. **Name the next command**: one of `/hero-1-research`, `/hero-2-write`, `/hero-3-check`, `/hero-4-publish` — or the specific unblocking action (e.g. "apply the pack corrections at the top of the wave-state file before launching wave N+1").

## Hard rules (all earned by defects in production use)

- **Always read the current wave-state file before resuming work** — never resume from a handover or this skill alone; a handover's stated counts have been wrong before
- Never launch a new wave while the previous wave's "upstream pack corrections owed" list is non-empty
- The pipeline's stage prompts live in the project's `prompts/` directory (R1/R2/R3/WRITER/CHECKER/FIXER) — agents are launched with "Follow ALL instructions in <prompt file>" + parameters, never with inlined rules
