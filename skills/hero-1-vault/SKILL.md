---
name: hero-1-vault
description: Stage 1 of the Project Hero pipeline — interactive batch build of the per-spec-point Obsidian vault, keyed to the Cobalt structure ratified at /hero-0-setup. Also handles adopting a pre-existing vault. Requires project.json from /hero-0-setup.
user_invocable: true
---

# /hero-1-vault — vault build (stage 1)

Builds an Obsidian vault for a course using **NotebookLM + the Cobalt course structure ratified at `/hero-0-setup`**. House style, exam-board conventions, and accept/reject rules are all inferred from NotebookLM during the build — no external reference vault is required.

**Requires `/hero-0-setup` to have run**: `project.json` (the single source of truth), `cobalt-structure.json` and `sp-mapping.json` must exist. If they don't, stop and send the user to `/hero-0-setup`.

**Vault structure: one file per Cobalt spec point.** Each subtopic typically contains 3–6 spec points; each spec point gets its own file named `[Section.Topic.Subtopic.SP] [SP name].md` (4-level decimal numbering — e.g. `1.1.1.1 Atomic structure.md`), with numbering and names taken from the ratified Cobalt tree — never from a tracker or a previous course. Obsidian's alphabetical ordering then puts files in spec order, and each file maps to its CMS spec point by construction (no reconciliation stage later). Spec points marked `no_content` in `sp-mapping.json` (e.g. video placeholders) get **no vault note** — they are correctly empty by ruling.

**Content shape per SP:** spec text, examiner-report citations (verbatim, paper code + tier + date), exam-appearance commentary (where/how the SP is examined), and subject-specific skills (the Q3 focus below). Depth benchmark: enough that a content creator never needs to reopen the source PDFs for routine drafting.

## DO NOT FABRICATE

The single most important rule of this skill. Every examiner-report quote, paper code, mark tariff, command-word pattern, candidate-error description, and statistic in the vault MUST be grounded in a named NotebookLM source — verbatim where quoted, faithfully paraphrased where summarised. **Never invent, never embellish, never fill gaps with plausible-sounding content.**

If NLM returns nothing for a spec point, write *"No examiner-report data available for this spec point in the current notebook."* That is the correct output. A gap left honest is infinitely better than a gap papered over with fabricated text — fabricated content gets shipped to students, treated as exam board guidance, and is impossible to clean up after the fact.

This rule binds **every writer agent** spawned in Step 10. When dispatching agents, the prompt must include this rule explicitly. The Step 11 spot-check exists precisely to catch fabrication: a single fabricated quote is grounds to audit the entire batch.

## How This Skill Works

Walk the user through setup interactively, one step at a time. Do not dump all instructions at once. Ask questions, wait for replies, then proceed.

## Step 0: Resume Check

Before anything else, read `project.json` (ask for the project directory if it isn't the current one) and check the `vault` block.

- **`vault.status: building`** → confirm to the user: "Resuming **[Course]** at SP **[next SP]** ([done]/[total] SPs complete). Last batch: **#[N]**." Skip directly to Step 10 — start by asking *"How many spec points would you like to do in this batch?"* (`_RESUME.md` in the vault root is a generated human-readable view of the same state — if it disagrees with `project.json`, `project.json` wins.)
- **`vault.status: complete` or `adopted`** → nothing to do here; point the user at `/hero-2-research`.
- **No `project.json`** → stop and send the user to `/hero-0-setup`.
- Otherwise → fresh build, continue from Step 1.

## Step 1: Confirm the Course

Read the course identity from `project.json` (board, qualification, subject, spec code — all captured at `/hero-0-setup`) and confirm: "Building the vault for **[Board] [Level] [Subject]** ([spec code]) — correct?" Do not re-ask what stage 0 already ratified; do stop if the user says it's wrong (fix `project.json` via `/hero-0-setup` first).

## Step 2: Set Expectations

Tell the user up front:

> I'll build the vault in batches that **you size**, confirming with you after each batch. I recommend starting with **3 SPs** for the first batch to verify the template is producing good output, then scaling up to **8–12 SPs** per batch once you're happy. With per-SP slicing handling context bloat (Step 10 step 4), larger batches amortise per-batch overhead better. Expect roughly **12–16 hours** of working time for a large course (~150 subtopics). Per-batch confirmation catches template drift early, and there's a final 5-claim spot-check at the end.

Always run with per-batch confirmation. Never run autonomously through to completion — the per-batch checks are the safety net that catches fabricated citations and template drift before they spread across the vault.

## Step 3: Verify the Stage-0 Handoff

Everything material was gathered at `/hero-0-setup` — verify it rather than re-gathering:

1. **Notebook**: `corpus.notebook_id` from `project.json`, verified live with `mcp__notebooklm__notebook_get` (title + source list — the notebook must contain past papers, mark schemes, examiner reports, the specification PDF and the extracted Cobalt content file; without them, citations will be thin or fabricated). If the MCP is unauthenticated, run its auth setup — browser sign-in once, cookies persist.
2. **Cobalt content file**: `paths.cobalt_content` points at a file that exists. The extraction is a stage-0 job (`/hero-0-setup` §6, which carries the extraction prompt). If the path is null WITH a dated ruling recorded there, the build proceeds without that layer by explicit decision. If it is null with no ruling, the extraction was missed: run `/hero-0-setup` §6 now (background agent or separate session — it is a big MCP crawl) and pause the build until the file lands.

3. **Structure**: `project.json` → `structure.ratified` has a date (the Cobalt-tree/CSV cross-check gate was passed). Never build against an unratified structure.
4. **Corpus conversion**: note `corpus.conversion.status` — it should be running or complete in the background; it does not block the vault build.

## Step 4: Adopt an Existing Vault (branch — skip for a fresh build)

If a per-SP vault already exists for this course (built before this pipeline, or by an earlier process):

1. List the vault directory and spot-open two notes. **Profile each against R1's nine extraction items** (spec text · exam-appearance table · ER insights with sitting attribution · MS conventions · subject skills or the no-skills marker · practical links · misconceptions · Cobalt commentary · notebook id in frontmatter) — record which are present and which are absent. Absences are declared research debt for wave 1, not an automatic fail; but a spec-text-only vault satisfies 1 of 9 and starves research, and this profile is what catches that.
2. Check filenames map onto `sp-mapping.json` (run `scripts/build_mapping.py` if names need reconciling — adopted vaults are the one case where mapping is not by construction).
3. Record `vault.status: adopted` + the coverage profile in `project.json`, and go straight to `/hero-2-research`.

## Step 5: Course Structure

The structure comes from `cobalt-structure.json` + `sp-mapping.json` — ratified at stage 0, cross-checked against the tracker there, with `no_content` spec points already ruled. Do **not** re-derive it from a tracker CSV or the specification PDF; if the user believes the structure is wrong, that's a `/hero-0-setup` re-ratification, not a local fix.

Report the shape so the user can sanity-check scale: sections, topics, subtopic count, SP count (minus `no_content` SPs = files to build).

## Step 6: Get Paper and Level Information

Ask:

> 1. **Paper codes and names** (e.g. H432/01 = Periodic table, elements and physical chemistry)?
> 2. **Which sections/topics map to which papers?**
> 3. **Level designations** (e.g. Sections 2–4 = AS, Sections 5–6 = A Level only; or Foundation/Higher; or Core/Extended)?
> 4. **Q3 focus**: after examiner reports (Q1) and exam appearance (Q2), Q3 fetches subject-specific skills that span multiple spec points. Default: **mathematical skills** for sciences and maths. For other subjects, common options:
>    - PE → practical/coaching skills, anatomical analysis
>    - English → literary techniques, language analysis frameworks
>    - History → source analysis skills, evidence-evaluation patterns
>    - Geography → fieldwork/data techniques, case-study application
>    - Economics → data interpretation, quantitative reasoning
>
>    Tell me what Q3 should focus on for this course, or say **"skip"** to omit Q3.

Save the Q3 focus into the Continuation Prompt **and `project.json` → `vault.q3_focus`** — writer agents need to know what's in Q3's batch data.

## Step 7: Choose Vault Location

Ask:

> **Where would you like the vault created?** Default is your Desktop, named `[Board] [Level] [Subject]`.

Record the chosen path as `paths.vault_notes` in `project.json` — the research stages read it from there.

## Step 8: Build the Vault

Confirm setup before building:

> **Ready to build:**
> - **Course**: [Board] [Level] [Subject] ([spec code])
> - **Vault location**: [path]
> - **Structure**: [X] subtopics / [Y] spec points from the ratified Cobalt tree ([Z] marked no-content and skipped)
> - **NotebookLM**: [notebook title, source count]
> - **Papers**: [list]
> - **Level designations**: [details]
>
> Shall I go ahead?

When confirmed:
1. Create the vault folder
2. Create `1. [Course Name] Course Structure.md` — all **spec points** as checkboxes with wiki links, grouped Section > Topic > Subtopic, **4-level decimal numbering** (1.1.1.1, 1.1.1.2, 1.1.2.1, …). Numbering and names come from `sp-mapping.json` (the ratified Cobalt tree): derive each SP number by counting spec points within their `(Section, Topic, Subtopic)` group. `no_content` SPs are listed but marked "no note — ruled no-content at setup", not given checkboxes
3. Create `[Course]-Continuation-Prompt.md` specifying: file naming convention `[Section.Topic.Subtopic.SP] [SP name].md` (one file per spec point), the structure source (`sp-mapping.json`), paper codes, level designations, NotebookLM notebook id
4. Initialise `project.json` → `vault`: `status: building`, `sps_total`, `sps_done: 0`, `next_sp`, `batches_done: 0`. Generate `_RESUME.md` in the vault root as a **human-readable view of that block** (course metadata, paths, notebook id, papers/levels, Q3 focus, progress) — regenerated after every batch, but `project.json` is the source of truth Step 0 reads

## Step 9: Test and Refine

> **Vault is set up. Let's test the template before scaling.** I'll create 2–3 test SP files from the same subtopic (so we can also check cross-SP linking). Say "go" when ready.

Run 2–3 SPs through the standard batch workflow. Then ask the user to check:
- Filename format (`1.1.1.1 [SP name].md`)
- YAML frontmatter (section, topic, subtopic, SP, level, papers, spec_text)
- Heading structure
- Examiner-report citation format (e.g. `8462/1H — 2024 June Examiner Report`)
- "How it appears in exams" usefulness
- Anything missing or in the wrong place

Iterate on the Continuation Prompt until they're happy.

## Step 10: Batch Building

Confirm: "Template approved. Starting batch building. **[Y] SPs total to build.**"

Then ask: **"How many spec points would you like to build in this first batch?"** Recommend **3 SPs for the first batch** so the user can verify the template is producing good output, then scaling up to **8–12 SPs** for subsequent batches. The user picks the size for every batch — never assume a default, never run autonomously through to completion.

Batch unit: **user-chosen number of SPs per batch (call this N).** NLM queries take the list of SPs in the batch — writer agents then write one file per SP, sharing the batch's NLM data. Stop and confirm with the user after each batch, asking how many SPs to do next.

For each batch:

1. Identify the next N unchecked SPs from the Course Structure page (where N is the count the user gave for this batch).
2. Run **one combined NotebookLM query via the MCP** with the `notebook_id` (from `project.json`) and the combined prompt below. **Recommended batch size: 8–12 SPs** once the rhythm is established (3 for the first batch). NLM responses to the combined query stay rich at this scale; if you see thinning, retry per the fallback in "Expected NotebookLM behaviour" below.

**Combined Query** — substitute `[Q3 focus]` with the value configured at Step 6 (omit Section 3 entirely if user said "skip"):

> For these spec points: [list of SPs in the batch, one per line, with their full text]
>
> Please give me **three sections, clearly separated**:
>
> **## Examiner Reports**
> All examiner report information linked to these spec points. Include the date of each examiner's report. Verify paper dates against document names.
>
> **## Exam Appearance**
> Where these spec points show up in past papers — front of paper or end of paper? Command words and question types used? Mark tariffs? Verify dates against document names.
>
> **## [Q3 focus] (per spec point)**
> For each SP above:
> - If [Q3 focus] applies, cross-reference with the specification and tell me which skills are needed and how they appear in exams.
> - If [Q3 focus] does **not** apply, simply respond: *"No [Q3 focus] for [SP number]."*

The per-SP conditional framing in Section 3 prevents stalls on qualitative batches — NLM returns clean per-SP negatives instead of an over-specified "system was unable to answer" failure.

3. Save the full MCP response to `batch-data/batch-NN.md` in the vault.
4. **Slice context per SP.** For each SP in the batch, create `batch-data/batch-NN-[SP-number].md` containing only that SP's content:
   - The SP's chunks extracted from each of the three sections of `batch-NN.md` (Examiner Reports / Exam Appearance / [Q3 focus])
   - That SP's entries extracted from `[Course]-Cobalt-Content.md` (the per-SP-grouped Cobalt commentary file)
   - That SP's entry from the ratified structure (`sp-mapping.json`: number, verbatim SP name/spec text, subtopic) — so the agent never has to scan the full structure files

   Each per-SP slice is typically **~2–3k tokens** vs the ~16k full batch + ~100k full Cobalt file + full structure. This single file is everything the writer agent needs beyond the template.
5. Spawn N parallel agents — one per SP in the batch. **The spawn prompt is minimal: it references the Continuation Prompt and the per-SP slice by path (the agent reads both with the Read tool), and embeds only the DO NOT FABRICATE rule verbatim.** This keeps the orchestrator's spawn-prompt cost tiny — N × ~500-token spawn prompts instead of N × ~3k embedded templates. Agents must NEVER read the full `batch-NN.md`, the full Cobalt commentary file, or the full structure files — only their own slice.
6. Tick the N SP checkboxes for the built SPs in the Course Structure page.
7. **Update `project.json` → `vault`**: increment `sps_done` and `batches_done`, set `next_sp` to the first remaining unchecked SP; regenerate the `_RESUME.md` view in the vault root to match. This is the state the next session's Step 0 reads.
8. Report progress (e.g. "Batch complete: N SPs built. Total: Y/X SPs done.") and ask: **"For the next batch, would you like to start a fresh session (recommended for token efficiency) or continue here?"**
   - If **fresh session**: tell the user to exit this session, start a new Claude Code session in the project directory, and run `/hero-1-vault` — Step 0 reads `project.json` and picks up at this batch loop. Each batch in its own session keeps token cost low.
   - If **continue here**: ask "How many spec points in this batch?" and proceed.
   - If **"stop"**: pause and let the user know they can resume any time via Step 0.

### Expected NotebookLM behaviour (handle without panicking)

With the combined query, NLM should return all three sections in one response. If the response is thin, missing a section, or returns *"The system was unable to answer."*:

- **First retry**: split the batch in half and run each as its own combined query (~2–3 SPs each).
- **If still thin**: fall back to running Examiner Reports, Exam Appearance, and the per-SP Q3 conditional as three separate queries. More verbose, but gives NLM more room per section.
- **As a last resort**: skip Section 3 (Q3) for this batch and flag it. Writer agents can infer subject-specific skill content from the spec text. Never run a batch with no examiner-report or exam-appearance data — those are core.

## Step 11: Spot-Check Verification

When all SPs are built, run a 5-claim verification before declaring done. This is the safety net that catches fabricated quotes.

1. **Pick 5 random SP files** across different sections (one per topic ideally).
2. **For each, identify one verifiable claim** — typically an examiner-report quote with paper code + tier + date (e.g. *"8462/1H — 2024 June Examiner Report: Some stated that potassium has more outer shells than sodium…"*).
3. **Query the NotebookLM MCP** with the `notebook_id` (from `project.json`) and the prompt: *"In the [paper code] [year/session] examiner report, what does it say about [topic]? Quote exact wording and cite the source document name."*
4. **Mark each PASS / DISCREPANCY / NLM-CANNOT-CONFIRM.**

Report: "**Spot check: X/5 PASS.**"

- **5/5 PASS**: ship.
- **Any FAIL**: audit the rest of that batch's notes immediately. The writer agent for that batch may be fabricating.
- **NLM-CANNOT-CONFIRM**: not a fail, but worth flagging so the user can manually verify if needed.

## Step 12: Hand Off to Research

When all SPs are built and the spot-check passes:

1. Set `project.json` → `vault.status: complete` and regenerate the `_RESUME.md` view one last time
2. Check `corpus.conversion.status` — if the background conversion from stage 0 isn't `complete` yet, say so: it gates `/hero-2-research`
3. Tell the user: "Vault complete: [Y] spec-point notes. Next: `/hero-2-research` for wave 1."

If a vault was built with an older callout-heavy template, strip `[!tip]`, `[!warning]`, `[!important]`, `[!info]`, `[!note]`, `[!todo]` callouts and decorative emojis, preserving equations and core content — the notes should be plain markdown before research begins.

## Key Rules

- **Be conversational** — one question at a time, never overwhelm
- **Confirm before building** — always show a summary and get approval before creating files
- **Course identity and structure come from `project.json`** — confirm them with the user, never re-derive from history, memory, a tracker or the spec PDF; structure disputes go back through `/hero-0-setup` re-ratification
- **NotebookLM queries go through the MCP** — returns response text only; notebook creation and source uploads happened in the NLM web UI at `/hero-0-setup`
- **Never invent NLM content** — only use what NLM returns. If no data: write *"No examiner-report data available for this spec point in the current notebook."*
- **Cite sittings precisely** — paper code + tier + date (e.g. `8462/1H — 2024 June Examiner Report`), not file names
- **Save progress to memory** so the conversation can be resumed in a new session
- **`project.json` → `vault` is the source of truth for resumption** — initialised at Step 8, updated after every batch (Step 10 step 7), read at Step 0 to skip Steps 1–9 entirely. `_RESUME.md` is a generated view for humans browsing the vault; never edit either by hand mid-build, and `project.json` wins any disagreement.
- **Per-SP context slicing** — writer agents NEVER read the full `batch-NN.md` (NLM batch data), the full Cobalt commentary file, or the full structure files. All three are pre-sliced into a single per-SP file in `batch-data/`. Each agent reads only its own ~2–3k slice. This is enforced in Step 10 step 4–5.
- **Spawn prompts reference, don't embed** — the Continuation Prompt (writer-agent template) lives in `[Course]-Continuation-Prompt.md`. Spawn prompts pass the file path; agents read it with the Read tool. Only the DO NOT FABRICATE rule is embedded verbatim (it's short and critical). This keeps the orchestrator's per-batch spawn-prompt cost minimal.
- **One batch per session is the recommended workflow** — the resume mechanism makes this seamless. Each new session reads ~500 tokens of resume state instead of accumulating thousands of tokens of conversation history. Continuing in-session is fine for quick consecutive batches but not recommended for the bulk of a build.
- **Plain markdown only** — use `## Headings`, paragraphs, and bulleted lists. Do **not** use Obsidian callouts (`> [!info]`, `> [!note]`, `> [!todo]`, `> [!tip]`, etc.) anywhere in note templates or generated content. Decorative emojis (✅, ⚠️, etc.) should not appear in body text.
- **Cobalt Commentary as summary, not dump** — if a Cobalt Commentary section is appended post-build (from an extracted commentary file), each subtopic gets a synthesised **5–8 bullet summary** of recurring themes across the question parts tagged to that subtopic. Never dump verbatim per-part bullets into the vault note.

## Out of Scope

The following are **not part of the Project Hero vault build** and should not be required from the user. If they have them and want to use them, fold in; if not, proceed without:

- **House style / formatting reference pages** — Claude infers conventions from mark schemes via NLM
- **Smart Mark Guidelines** — only relevant later when writing mark schemes for the Cobalt CMS
- **Cobalt CMS exports** (Commentary, MS&G, ET&T) — only if enriching notes with existing CMS content; must be checked for accuracy first
