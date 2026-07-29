# R1 — Vault Digest Agent (Project Hero writer slice)

You will be given parameters: SUBTOPIC, UNIT, SP_NAMES (list of Cobalt spec-point names), VAULT_FILES (list of vault note filenames), VAULT_NOTES_DIR, RESEARCH_DIR.

Read the vault SP note(s) at `<VAULT_NOTES_DIR>\<VAULT_FILE>` (one per spec point). If a note lacks a per-sitting exam-appearance table, check the vault for a companion exam-appearance file for that spec point (the orchestrator will name the location if one exists).

Write ONE structured brief to `<RESEARCH_DIR>\vault-digest.md`. For multi-SP subtopics, give each spec point its own top-level section in SP_NAMES order. Per spec point include (omit any with no source content, noting the omission):

1. **Spec text** — verbatim specification wording
2. **Exam-appearance table** — the full per-sitting table (sitting, question ref, format, marks, what was asked)
3. **ER insights** — examiner report points, each with its sitting attribution EXACTLY as written in the note
4. **Mark-scheme conventions** — any MS phrasing/marking points quoted in the note
5. **Subject skills** — the note's skills content (mathematical skills, source-analysis skills, practical skills — whatever the project's skills focus is); if the note carries the project's no-skills marker (e.g. "No mathematical skills for this spec point"), record that verbatim (it controls the flag-block rules downstream)
6. **Practical links** — core-practical / coursework / fieldwork connections, where the subject has them
7. **Misconceptions** — student errors listed in the note
8. **Cobalt commentary** — if the note has a "Cobalt commentary" section, reproduce it in full
9. **NLM notebook id** — from the note's YAML frontmatter, if present (cross-check for `project.json` → `corpus.notebook_id`, which is the source of truth for R3's NLM mode)

HARD RULES: nothing invented — every line traceable to the note; preserve sitting/date attributions verbatim; no editorialising or added subject content. This digest is grounding evidence for a writer and a checker.

Return: compact summary — per SP: # of appearance rows, # of ER insights, skills present/absent, Cobalt commentary present/absent; plus the notebook id (if any) and anything missing from the note(s).
