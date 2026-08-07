# Writer-Agent Enrichment Slice — pipeline blueprint

The per-subtopic pipeline that turns wave research into a template-compliant enriched knowledge file. One slice = one subtopic. Slices are independent — run in parallel batches (waves).

## Model mix (ratified after a 5-subtopic calibration wave on the pilot course)

| Stage | Model | Rationale |
|---|---|---|
| R1 / R2 / R3 / fix-editors / RN-pull / uploader | Sonnet | Mechanical extraction, verification and edits — verification gates held at this tier (caught NLM misattributions + vault-note citation errors) |
| Writer | Opus | Register verified indistinguishable from a strongest-tier sample in line diff; heavily scaffolded by evidence packs |
| Checker | Strongest available, never below Opus 5 | The safety net. Pilot-course process-review verdict: Opus 5 checkers were NOT demonstrably inferior to the strongest tier — blind re-audits found comparable miss rates under both. Spend scarce top-tier budget on the sampled re-audit stage instead |

Calibration result: roughly a 3× cost reduction at equal output quality versus all-strongest-tier. Calibration blockers were citation/quote-integrity only — but later waves caught genuine subject-content errors at checker stage, so never assume writers only make citation errors.

## Inputs (resolved by orchestrator, no agent needed)

| Input | Source |
|---|---|
| Subtopic id, name, section, topic, unit, SP ids + names | `sp-mapping.json` `subtopics` |
| Spec text per SP | `sp-mapping.json` `mapping` (verbatim; converted specification as fallback) |
| Skills entry per SP | `skills-map.json` (`paths.skills_map` — direct spec read at stage 0) |
| Cobalt commentary per SP | `paths.cobalt_content` (extracted at stage 0; null only by dated ruling) |
| Legacy vault note file(s) per SP | adopted-vault courses only: `sp-mapping.json` `mapping` (`vault_file` per `cobalt_sp_id`) |
| Cobalt RN content | `searchRevisionNotes(subtopic_id)` → `findRevisionNote` — save to research folder; flag any `$c{` commentary blocks (they carry examiner-style guidance to fold in) |
| Board conventions | One extraction per course (`prompts/BOARD-CONVENTIONS.md`, run as the CLOSING act of wave 1's `/hero-1-research` → `paths.board_conventions` — F29/F31; `/hero-2-write` asserts the path and refuses on null): command words from the spec's own taxonomy appendix, marking-grid conventions from the Additional-guidance column, traps from ERs. Reused every slice, never re-derived |
| Tier flags | `sp-mapping.json` per-SP `true \| false \| "partial"` + note (F50/F56) — passed to writers as HIGHER_TIER_ONLY; tier is never inferred from paper appearances or the converted spec |
| Exemplars | `project.json` → `exemplars` + the project README's template rules block |

Working files: `research/<unit-key>/<Subtopic>/` — `rn.md`, `vault-digest.md`, `ms-extracts.md`, `nlm-check.md`. Kept as grounding evidence for proofing.

## Stage R — research

**R1 — evidence assembly** (read-only agent, `prompts/R1-evidence-assembly.md`)
Assembles the subtopic's grounding brief (`vault-digest.md` — filename kept for pack compatibility) directly from the stage-0 artifacts: verbatim spec text per SP (sp-mapping), the skills entry or no-skills marker (skills-map), and the Cobalt commentary slice. Exam-appearance, ER and MS evidence are explicitly deferred to R2/R3 — never pre-filled. Nothing invented — everything traceable to a named artifact. *(Adopted-legacy-vault courses run `prompts/R1-vault-digest.md` against the vault notes instead; vault content is leads to verify, never ground truth.)*

**R2 — MS/QP discovery + verbatim extraction** (read/grep agent on the corpus)
Builds the per-sitting appearance record itself — enumerating every sitting in the unit's corpus and sweeping each QP/MS for the spec points — then extracts verbatim question stems (QP) and verbatim MS marking points for the strongest worked-example and marking-point candidates. Rules: per-file `grep -c` for any count claim; corrupted conversions recovered from MS example calculations; every worked-example number verified against the MS. Two conversion gotchas produce false "no evidence exists" results: **ER header forms** vary within a corpus (`Question 18` vs `Q18(a)` vs `Q18 (a)` vs `Q 15 (a)`) so absence must be tested against every form; and **`## Page N` markers split paragraphs** — a quote running to a page end must be continued past the marker.

**R3 — examiner-insight cross-check.** Two modes; `project.json` → `research_mode` decides (**local is the default**; NLM remains available as an escalation when a local sweep runs thin, and for courses without a converted ER corpus):

*R3-LOCAL (default — `prompts/R3-local-check.md`):* a systematic per-sitting ER sweep of the local corpus. Everything emitted is a verbatim quote with a file/line ref by construction, so extraction and verification are the same act and the NLM-mistranscription defect class (wrong MCQ answers, invented marking points, inverted facts) cannot occur. Same output filename and section skeleton as the NLM variant — downstream stages unchanged. **Hard gate: R2 must have finished first** (the coverage diff in section 4 is meaningless otherwise).

*R3-NLM (escalation/legacy — `prompts/R3-nlm-check.md`):* queries NotebookLM. Any attribution NOT already in R1's brief must be verified against the local corpus before it may be cited; unverifiable items are reported as "unverified — do not cite". Two gates on top of sitting/topic agreement:
- **Apparatus/set-up gate:** whenever NLM characterises a question, open the QP and confirm the set-up matches — apparatus/source named, geometry/framing, and the quantity actually asked for. Sitting and topic both checking out is not enough (on the pilot course, two diffraction-*grating* questions reached the writer as "double-slit")
- **Mark-scheme coverage gate (applies in BOTH modes):** R3's verified insights can introduce question refs R2 never extracted, so the pack looks fully grounded while nobody has read those tariffs. R3 must diff its refs against `ms-extracts.md` and report the uncovered ones (section 4 of `nlm-check.md`) for the orchestrator to top up before the writer runs. On the pilot course, both of one file's blockers came from this gap

## Stage W — writer (1 agent, `prompts/WRITER.md`)

Composes the master `.md` per the project's template rules using: R1–R3 briefs + RN content + exemplars. Highlights (full rules in the prompt):
- Key-concept H3s derived from the research (not a fixed list); student-friendly polished prose; worked examples with MS-verified numbers and provenance visible on the page (attributed sitting + ref, or genuinely invented — never a past-paper question presented as invented)
- Flag block per spec point (Key terminology always; the course's skills line only where genuine)
- First-appearance definitions for every flagged term, per spec point
- Contextualise-first: key point + actionable strategy in our own words, verbatim MS/ER quote after as evidence
- Quote integrity: quotation marks ONLY around verbatim pack text; never edit inside a quote
- No manufactured certainty: only assert what the pack literally states; hedge honestly otherwise. This is advice that costs students marks, so it outranks quote integrity in severity
- Self-check before returning: definitions, notation consistency, certainty audit, direction audit, symbol sweep

Output: master file at `knowledge-files/<unit-key>/<Subtopic>.md` (callouts kept — proofing markers).

## Stage V — verify + package (orchestrator + agents)

1. Checker agent (`prompts/CHECKER.md`) audits the draft against the fixed checklist; writes `checker-report.md`
2. Fix findings (fixer agent per checker report + orchestrator rulings)
3. **`fixer_diff_sweep.py` on every fixer-touched master** — scans only the lines the fixer ADDED (git diff vs the pre-fixer state) for manufactured-certainty patterns and new quoted spans. Report-only on hits: each is a read-before-strip candidate for the orchestrator. **Exit 2 = `GATE COULD NOT RUN` (no git baseline) and the step is NOT satisfied (F63)** — commit the pre-fixer masters first. Why the gate exists: a pilot-course fixer *introduced* a false "every time" claim after the checker signed off, and it shipped
4. **Blind re-audit** — after the wave's fix cycle: **every file on the course's first wave (F55 ruling); 2–3 risk-picked files on waves 2+** (dense sibling clusters, inferred figure content, heavy calculation) — a FRESH checker pass by an independent agent, blind to the original `checker-report.md` **and to contested rulings (F57 — a ruling in its brief makes the re-audit a second signature, not a second opinion; pass the ruling's evidence or withhold it)**, writing to `re-audit.md`. Findings go through the normal ruling → fixer → diff-sweep path. Calibration: pilot ~10 actionable findings per re-audited file; 1PH0 wave 1 13.3, every sampled file carrying a blocker its original checker missed — yield independent of the original checker's model, the highest-yield quality step per token this pipeline has measured
5. `preflight_sweep.py` on the masters — mechanical FAIL checks (U+1D400 chars, escaped `Q\*` counted at byte level, `\Delta`, `$c{`, images, http links, flag-block parity) plus the Oxford-comma list-candidate report; fix all FAILs and review every Oxford hit before stripping
6. `protect_starred_refs.py`, then `strip_for_cobalt.py` → `.cobalt.md`, then `preflight_sweep.py --cobalt` on the stripped variants (adds callout/blockquote checks). Validate the skills-line total against the wave's OWN skills-omission ruling list — never a handover's stated expectation
7. **HOLD** — no upload until the user proofs the sample. Upload step (createDocument + manifest) runs only after approval

## Failure modes to watch (from pilot experience)

- Grep count fabrication → per-file counts only (house rule)
- NLM date misattribution → local verification gate in R3
- Template drift → checker compares section skeleton to the ratified template, and prose register to the exemplars
- Duplicate SP names across units → R2 is scoped to the subtopic's own unit corpus; headings come from Cobalt structure for the right subtopic id
- Orchestrator cautions can be wrong → word every caution/EXTRA_CHECK as directed attention that invites escalation, never as a deletion order; the paper outranks everything
