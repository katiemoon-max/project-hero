# Project Hero — <Board Qualification Subject> → Cobalt Export

Converting the completed <course> vault (<N> spec-point notes at `<vault_notes path>`) into Cobalt course knowledge files and uploading them to the docs store on course `<crs_...>`.

## Pipeline

1. `scripts/build_mapping.py <structure-dump.txt>` — parses a `getCourseStructure` dump + vault frontmatter → `sp-mapping.json` + `mapping-report.md`. Target state: every SP matched, 0 ambiguous. Name normalisation folds curly apostrophes; genuine name differences go in the script's ALIASES map (Cobalt names are authoritative — no vault rename needed for export)
2. Per-wave research → write → check → publish via the `/hero-1` … `/hero-4` skills, using the stage prompts in `prompts/`
3. **Strip for Cobalt**: `scripts/strip_for_cobalt.py <file.md>` → `<file>.cobalt.md`. The Cobalt doc viewer renders plain markdown only — Obsidian callouts and blockquotes show as literal `>` text. The script converts `[!tip]`/`[!warning]` callouts to headings one level below their section (warnings suffixed " (Common Error)") and unquotes everything incl. the `> **Specification:**` lines. **Vault masters KEEP callouts** (proofing markers); only the `.cobalt.md` variant is uploaded
4. Upload the `.cobalt.md` content: `createDocument` per file (title = subtopic name), record `document_id` in the manifest, read chunk/warning summary. Fixes go through `updateDocument` with the whole file — **never create twice** (duplicates; no delete API)

## Conversion rules

- Frontmatter: `section:` / `topic:` / `subtopic:` verbatim Cobalt names (precise scoping; avoids duplicate-SP-name traps across units), `tags: [<subject_slug>, project-hero]`
- `# Sub-topic: <name>` / `## Spec Point: <name>` — names verbatim from Cobalt structure, never from vault filenames
- Spec text stays as the `> **Specification:** …` quote under each spec point heading

## Template rules — research-driven key concepts

Content is written **student-friendly and polished, as if read by a student preparing for the exam** — full explanations, not brief notes; worked examples where relevant.

```
# Sub-topic: <sub-topic>
## Spec Point: <spec point>          ← exact spec text as > **Specification:** quote beneath
**Key terminology:** …               ← flag block directly under the spec quote
**<skills_line_label>:** …           ← only where the spec point has genuine skills content; omit otherwise
### <Key concept 1>
### <Key concept 2> …                ← concept list comes from RESEARCH, not a fixed section list
### How <Spec Point> Appears in Exams
#### <exam_skeleton entry 1>         ← one H4 per entry in project.json → template.exam_skeleton
#### <exam_skeleton entry 2> …          (ratified at /hero-0-setup step 3 — the template check gate)
#### Command Words for <Spec Point>  ← table: command word | what to do | common traps
#### Exam Strategy for <Spec Point>  ← [!tip] strategies + mark-scheme conventions + [!warning] errors
```

Worked example of `template.exam_skeleton` (from the sciences pilot — an exemplar of the *shape* only, never values to copy: some courses have no sections at all, MCQs interspersed as ordinary parts): `"Multiple Choice (Section A)"` · `"Structured Questions (Section B)"` · `"Levelled 6-Mark Questions (Section B)"`. Ratify your course's real skeleton at `/hero-0-setup` §3.

Rules:
- **Key concepts are derived per course by research** (local QP/MS/ER corpus + Cobalt RN + ER cross-check) — the same spec point gets a different concept structure on different courses
- Under each key concept: everything a student needs for the exam, as explanations with worked examples (real past-paper numbers verified against the MS, or clean invented numbers in exemplar style)
- Woven in **where relevant, never shoehorned**: `[!tip]` teaching points (the WHY), `[!warning]` misconceptions/errors tied to ER citations
- **Contextualise all exam-board material: lead with the key point and an actionable strategy in our own words; the verbatim MS/ER quote follows as supporting evidence — never quote-first.** Applies to callouts and body prose alike (MS point lists become "to score full marks, make each of these points…")
- **ER citations as sitting + paper only** (e.g. "October 2022 Unit 1") — never file names. Question refs as full-month + main question number only, no part letters: "June 2023 Q17"; starred refs as "Q*14" (UNESCAPED — see standing rule below)
- **Exam-section structure:** MCQ-type sections = **Typical questions** / **Common question types** / **Common distractors**. Structured sections = **Typical questions**, then one **"Question format — <Command word/type> (N marks)"** block per format, each with **Example — <sitting> Qn:** and **Marking points:** taken from the real MS plus a contextualising takeaway line. Levelled/extended-response sections (where the course has them) = **spec-point-specific only** — the board's generic levelled scoring mechanism is EXCLUDED; it lives in a separate general exam-advice knowledge file not tied to a sub-topic
- Skills and practical content **integrated contextually** (graphs under a graphs concept, practicals under a measurement concept) — no separate skills section; no Key takeaways section
- **Flag blocks per spec point:** immediately after each `> **Specification:**` quote, a `**Key terminology:**` line (5–10 load-bearing terms from that spec point's own content, " · " separators, lower case unless proper noun) and — only where the spec point has genuine skills content — a `**<skills_line_label>:**` line (3–6 concrete exam skills in the file's own notation). Strictly scoped to the spec point (no cross-SP or cross-topic bleed); no terminal punctuation
- No emoji/✅✗ (house style); callouts restricted to `[!tip]`/`[!warning]`
- The per-sitting exam-appearance table **stays in the process** (vault notes keep it; writers use it as grounding) but is not emitted in the final file

## Standing rules (earned in production)

- **Starred question refs are UNESCAPED.** Write `Q*17`, never `Q\*17` — Cobalt renders markdown verbatim, so the backslash shows literally to students. The asterisk is protected instead by **bolding the Example label** (`**Example — October 2024 Q*17:**`) so the ref's asterisk cannot open an emphasis run, with `scripts/protect_starred_refs.py` as the build-time guard
- Frontmatter values containing colons must be double-quoted or the upload breaks
- Re-running any mechanical converter on a hand-enriched file clobbers it — writer-agent output is the master

## Status

- [ ] Recon: course structure fetched, mapping green
- [ ] Template check ratified (exam skeleton in project.json)
- [ ] Pilot subtopic authored, proofed and approved
- [ ] Wave 1 …
