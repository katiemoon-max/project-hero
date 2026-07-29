---
name: hero-4-check
description: Stage 4 of the Project Hero pipeline — wave checking. Launches adversarial checker agents (strongest-model tier) per drafted subtopic, adjudicates escalations by reading the papers, then launches fixer agents per report. The quality gate before publish — never trimmed, never downgraded below Opus 5.
---

# /hero-4-check — checkers, rulings, fixers

Read `project.json` and the wave-state file. Checker model: strongest available per project policy (never below Opus 5). Fixers: research tier (default Sonnet).

## Per drafted subtopic

1. **Checker**: "Follow ALL instructions in `prompts/CHECKER.md`" + parameters, including EXTRA_CHECKS assembled from the wave-state file (cluster boundaries, named exclusions, ref lists for the tariff-coverage rule — the more specific the brief, the more real defects surface). EXTRA_CHECKS are **directed attention, never deletion orders**.
2. **Adjudicate escalations — by reading the paper.** When a checker disputes a pack rule, an EXTRA_CHECK, or another agent's claim: the QP/MS text outranks every derived file and every orchestrator instruction. Never average two agents. Record each RULING in the wave-state file with the paper evidence. When a blocker traces upstream (digest/ms-extracts/nlm-check), correct the pack at source with a dated bracketed note — never inside verbatim quotes.
3. **Fixer**: "Follow ALL instructions in `prompts/FIXER.md`" + the checker report + any orchestrator rulings (including "do NOT apply finding X" where overruled). Fixers report per-item application; chase any item reported unapplicable.
4. **Fixer-diff re-sweep**: `scripts/fixer_diff_sweep.py` on every fixer-touched master — scans only fixer-ADDED lines (git diff) for manufactured-certainty patterns and new quoted spans. Report-only; orchestrator eyeballs each hit. This gate exists because a fixer once introduced a false absolute claim after checker sign-off, and it shipped.
5. **Sampled blind re-audit**: after the wave's fix cycle, 2–3 files (risk-picked: dense sibling clusters, inferred figures/diagrams, calculation-heavy) get a fresh checker pass by an independent agent, blind to `checker-report.md`, writing `re-audit.md`. Findings go through the normal ruling → fixer → diff-sweep path. Calibration from the pilot build: ~10 actionable findings per re-audited file, yield independent of the original checker's model — the pipeline's highest-yield quality step per token.

## Wave-state bookkeeping

Blocker/fix/note counts per file; blocker-class tally (manufactured certainty, quote integrity, factual/data, symbols, direction) — this is the metric record that process reviews depend on; note the checker MODEL actually used per file (session-kill substitutions happen and matter later).

Next: `/hero-5-publish` once all wave files are fixed.
