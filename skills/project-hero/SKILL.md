---
name: project-hero
description: Interactive guided setup for building a Project Hero Obsidian vault. Walks the user step by step through gathering materials, setting up NotebookLM, creating the vault, and starting the batch workflow. Use when someone wants to build a new Project Hero vault from scratch.
user_invocable: true
---

# Project Hero Vault Builder

Builds an Obsidian vault for a course using **NotebookLM + the course's Master Syllabus CSV**. House style, exam-board conventions, and accept/reject rules are all inferred from NotebookLM during the build — no external reference vault is required.

**Vault structure: one file per spec point.** Each subtopic typically contains 3–6 spec points; each spec point gets its own file named `[Section.Topic.Subtopic.SP] [SP name].md` (4-level decimal numbering — e.g. `1.1.1.1 Atomic structure.md`). This is so Obsidian's alphabetical ordering puts files in spec order, and so each file maps cleanly to a single CMS spec point on export.

**Content shape per SP:** spec text, examiner-report citations (verbatim, paper code + tier + date), exam-appearance commentary (where/how the SP is examined), and subject-specific skills (the Q3 focus below). Depth benchmark: enough that a content creator never needs to reopen the source PDFs for routine drafting.

## DO NOT FABRICATE

The single most important rule of this skill. Every examiner-report quote, paper code, mark tariff, command-word pattern, candidate-error description, and statistic in the vault MUST be grounded in a named NotebookLM source — verbatim where quoted, faithfully paraphrased where summarised. **Never invent, never embellish, never fill gaps with plausible-sounding content.**

If NLM returns nothing for a spec point, write *"No examiner-report data available for this spec point in the current notebook."* That is the correct output. A gap left honest is infinitely better than a gap papered over with fabricated text — fabricated content gets shipped to students, treated as exam board guidance, and is impossible to clean up after the fact.

This rule binds **every writer agent** spawned in Step 10. When dispatching agents, the prompt must include this rule explicitly. The Step 11 spot-check exists precisely to catch fabrication: a single fabricated quote is grounds to audit the entire batch.

## How This Skill Works

Walk the user through setup interactively, one step at a time. Do not dump all instructions at once. Ask questions, wait for replies, then proceed.

## Step 0: Resume Check

Before asking any setup questions, ask the user:

> **Are you resuming an existing Project Hero build?**
> - **Yes**: paste the path to the vault folder.
> - **No**: I'll start a fresh setup from Step 1.

If yes:
1. Read `[vault path]/_RESUME.md` — the structured pickup file written after every batch.
2. Confirm to the user: "Resuming **[Course]** at SP **[next SP]** ([done]/[total] SPs complete). Last batch: **#[N]** ended **[timestamp]**. Skipping setup."
3. Skip directly to Step 10 — start by asking *"How many spec points would you like to do in this batch?"*

If `_RESUME.md` doesn't exist or can't be parsed, fall back to fresh setup (Step 1).

## Step 1: Identify the Course

**ALWAYS ask the user this question fresh — do NOT assume any course details from the slash command, conversation history, or memory.** Wait for their reply before proceeding.

Ask the user:

> **What course are you building a vault for?**
> 1. **Exam board** (e.g. AQA, Edexcel, OCR, CIE, IB)
> 2. **Subject** (e.g. Chemistry, Biology, Physics, Maths)
> 3. **Level** (e.g. GCSE, IGCSE, A Level, IAL, IB)
> 4. **Specification code** if you know it (e.g. H032/H432, 4CH1, 8CH0)

Once they answer, confirm: "OK, I'll be setting up a vault for **[Board] [Level] [Subject]**."

## Step 2: Set Expectations

Tell the user up front:

> I'll build the vault in batches that **you size**, confirming with you after each batch. I recommend starting with **3 SPs** for the first batch to verify the template is producing good output, then scaling up to **8–12 SPs** per batch once you're happy. With per-SP slicing handling context bloat (Step 10 step 4), larger batches amortise per-batch overhead better. Expect roughly **12–16 hours** of working time for a large course (~150 subtopics). Per-batch confirmation catches template drift early, and there's a final 5-claim spot-check at the end.

Always run with per-batch confirmation. Never run autonomously through to completion — the per-batch checks are the safety net that catches fabricated citations and template drift before they spread across the vault.

## Step 3: Gather NotebookLM Sources

The Project Hero build relies on a NotebookLM notebook with **all the materials needed to ground examiner-report citations and exam-appearance evidence**. You'll need:

1. **Past papers** for the course (all available sittings)
2. **Mark schemes** matching those papers
3. **Examiner reports** matching those papers
4. **Specification PDF**
5. **Cobalt content** — commentary + Examiner Tips & Tricks extracted from the Cobalt CMS

Steps 10 (batch building) and 11 (spot-check verification) query NLM for examiner-report wording, paper codes, mark tariffs, and command words — these queries only work if past papers, mark schemes, and examiner reports are in the notebook. **Do not skip them** — without them, citations will be thin or fabricated.

**Sources 1–4 — Past papers, mark schemes, examiner reports, specification:**

Ask the user:

> **Do you have past papers, mark schemes, examiner reports, and the specification PDF for this course?**
> - **Where to find them**: The exam board website — search for your specification code.
> - If you have them, tell me the folder path.

**Source 5 — Cobalt content (commentary + Examiner Tips & Tricks):**

Ask the user:

> **Have you already extracted the Cobalt content for this course?** I need a markdown file containing:
> - **Commentary** (text wrapped in `$c{...}` in Cobalt — renders as blue text)
> - **Examiner Tips & Tricks** (the `**Examiner Tips and Tricks** ... **End of Examiner Tips and Tricks**` blocks)
>
> If **yes**: tell me the file path.
>
> If **no**: I'll give you a prompt to run in a separate Claude Code session to extract it. The extraction takes 20–40 minutes and uses a meaningful share of a session quota for a large course, so it's best done as a separate session before continuing here.

If they haven't extracted it yet, give them this prompt and pause until they've run it:

```
Extract all commentary and Examiner Tips & Tricks from [COURSE] in Cobalt.
Use the sme-content MCP. For every published question and question part, find:
- Commentary — text wrapped in $c{...} sequences (renders as blue text in the
	Cobalt UI). This is in the answer modal of structured questions.
- Examiner Tips & Tricks — text between **Examiner Tips and Tricks** and
	**End of Examiner Tips and Tricks**.
Organise the output as a markdown file grouped by spec point. For each entry,
include the spec point(s) it's tagged to and label it as "Commentary" or
"Examiner Tips and Tricks".
Save the file to my Desktop as [COURSE]-Cobalt-Content.md.
```

Wait for them to confirm extraction is done and tell you the file path before proceeding.

## Step 4: Set Up NotebookLM

Ask:

> **Do you already have a NotebookLM notebook for this course?**
> - **Yes**: paste the notebook URL.
> - **No**: I'll walk you through creating one (the NLM web UI handles uploads; the MCP handles queries).

### 4a. Authenticate the NotebookLM MCP

Check the NotebookLM MCP's health/auth status. If unauthenticated, run its auth setup — opens a browser tab, user signs in once, cookies persist for future sessions. After auth is done, no further sign-in is needed.

### 4b. If they need to create a new notebook (manual NLM web UI work)

The MCP supports queries but not PDF uploads, so notebook creation + source uploads happen in the NLM web UI:

1. Tell the user to go to [notebooklm.google.com](https://notebooklm.google.com) and create a new notebook.
2. Upload all the sources from Step 3 (past papers, mark schemes, examiner reports, spec PDF, Cobalt content). **Do NOT upload the Master Syllabus CSV** — that goes in the Obsidian vault only.
3. Rename sources to clear paper-code-based names (e.g. `8462-1H-2024-June-ExaminerReport.pdf`) — ambiguous source names cause fabricated citations downstream.
4. Copy the notebook URL and paste it here.

### 4c. Register the notebook with the MCP

Register the notebook URL with the MCP. Save the returned `notebook_id` — it's the handle Steps 10 and 11 use to query this notebook.

### 4d. Confirm completion

Tell the user: "NotebookLM is registered with the MCP. Notebook ID: [id]."

## Step 5: Get the Master Syllabus CSV

Ask:

> **I need the Master Syllabus CSV.**
> - **Where to find it**: Open your subject's exam board tracker (Google Sheets) → "Master Syllabus" tab → File > Download > CSV.
> - Save it locally and tell me the path.
> - If no tracker exists yet, I can generate the CSV from the specification PDF.

When they provide the path, read the CSV and report the column structure:

> Here's the column structure I found:
> - Column A: [header] — I'll use this as [purpose]
> - Column B: ... etc.
>
> Does this look right? Any columns I should know about (e.g. one marking Higher/Extended/A Level only)?

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

Save the Q3 focus into the Continuation Prompt — writer agents need to know what's in Q3's batch data.

## Step 7: Choose Vault Location

Ask:

> **Where would you like the vault created?** Default is your Desktop, named `[Board] [Level] [Subject]`.

## Step 8: Build the Vault

Confirm setup before building:

> **Ready to build:**
> - **Course**: [Board] [Level] [Subject] ([spec code])
> - **Vault location**: [path]
> - **CSV**: [path] ([X] subtopics)
> - **NotebookLM**: [URL]
> - **Papers**: [list]
> - **Level designations**: [details]
>
> Shall I go ahead?

When confirmed:
1. Create the vault folder
2. Copy the CSV into the vault
3. Create `1. [Course Name] Course Structure.md` — all **spec points** as checkboxes with wiki links, grouped Section > Topic > Subtopic, **4-level decimal numbering** (1.1.1.1, 1.1.1.2, 1.1.2.1, …). Derive each SP number by counting spec points within their `(Section, Topic, Subtopic)` group from the Master Syllabus CSV (first SP in subtopic 1.1.1 → `1.1.1.1`, second → `1.1.1.2`, etc.).
4. Create `[Course]-Continuation-Prompt.md` specifying: file naming convention `[Section.Topic.Subtopic.SP] [SP name].md` (one file per spec point), CSV column structure, paper codes, level designations, NotebookLM URL.
5. Create `_RESUME.md` in the vault root with course metadata, all paths, NotebookLM URL, **NotebookLM notebook_id (from Step 4c)**, papers/levels, Q3 focus, total SP count, and `Completed: 0`. This file gets updated after every batch and is the resumption source-of-truth read by Step 0.

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
2. Run **one combined NotebookLM query via the MCP** with the `notebook_id` (from `_RESUME.md`) and the combined prompt below. **Recommended batch size: 8–12 SPs** once the rhythm is established (3 for the first batch). NLM responses to the combined query stay rich at this scale; if you see thinning, retry per the fallback in "Expected NotebookLM behaviour" below.

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
   - That SP's row from the Master Syllabus CSV (so the agent never has to scan the full CSV)

   Each per-SP slice is typically **~2–3k tokens** vs the ~16k full batch + ~100k full Cobalt file + full CSV. This single file is everything the writer agent needs beyond the template.
5. Spawn N parallel agents — one per SP in the batch. **The spawn prompt is minimal: it references the Continuation Prompt and the per-SP slice by path (the agent reads both with the Read tool), and embeds only the DO NOT FABRICATE rule verbatim.** This keeps the orchestrator's spawn-prompt cost tiny — N × ~500-token spawn prompts instead of N × ~3k embedded templates. Agents must NEVER read the full `batch-NN.md`, the full Cobalt commentary file, or the full CSV — only their own slice.
6. Tick the N SP checkboxes for the built SPs in the Course Structure page.
7. **Update `_RESUME.md`** in the vault root: increment Completed count, update last batch number + timestamp, set "Next SP" to the first remaining unchecked SP. This is the pickup file the next session reads at Step 0.
8. Report progress (e.g. "Batch complete: N SPs built. Total: Y/X SPs done.") and ask: **"For the next batch, would you like to start a fresh session (recommended for token efficiency) or continue here?"**
   - If **fresh session**: tell the user to exit this session, start a new Claude Code session, run `/project-hero`, say **"yes"** at the resume prompt, and paste the vault folder path. The new session reads `_RESUME.md` and picks up at this batch loop. Each batch in its own session keeps token cost low.
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
3. **Query the NotebookLM MCP** with the `notebook_id` (from `_RESUME.md`) and the prompt: *"In the [paper code] [year/session] examiner report, what does it say about [topic]? Quote exact wording and cite the source document name."*
4. **Mark each PASS / DISCREPANCY / NLM-CANNOT-CONFIRM.**

Report: "**Spot check: X/5 PASS.**"

- **5/5 PASS**: ship.
- **Any FAIL**: audit the rest of that batch's notes immediately. The writer agent for that batch may be fabricating.
- **NLM-CANNOT-CONFIRM**: not a fail, but worth flagging so the user can manually verify if needed.

## Step 12: Export and Cleanup

> **All SPs built and spot-checked. Ready to export?**
>
> Standard process:
> 1. Notes were already built clean (plain markdown — no callouts, no decorative emojis), so export is straightforward.
> 2. The vault is already one-file-per-SP, so no splitting is needed for CMS upload.
> 3. If equations need a different syntax for the target platform, convert in this pass.

If a vault was built with an older callout-heavy template, strip `[!tip]`, `[!warning]`, `[!important]`, `[!info]`, `[!note]`, `[!todo]` callouts and decorative emojis, preserving equations and core content.

## Key Rules

- **Be conversational** — one question at a time, never overwhelm
- **Confirm before building** — always show a summary and get approval before creating files
- **Always ask Step 1 fresh** — never assume course details from history or memory
- **NotebookLM queries go through the MCP** — returns response text only; browser automation is only needed during initial setup if the user is creating a new notebook or renaming sources in the NLM web UI (Step 4b)
- **Never invent NLM content** — only use what NLM returns. If no data: write *"No examiner-report data available for this spec point in the current notebook."*
- **Cite sittings precisely** — paper code + tier + date (e.g. `8462/1H — 2024 June Examiner Report`), not file names
- **Save progress to memory** so the conversation can be resumed in a new session
- **`_RESUME.md` is the source of truth for resumption** — created at vault setup (Step 8), updated after every batch (Step 10 step 7), read at Step 0 to skip Steps 1–9 entirely. Never edit by hand mid-build.
- **Per-SP context slicing** — writer agents NEVER read the full `batch-NN.md` (NLM batch data), the full Cobalt commentary file, or the full CSV. All three are pre-sliced into a single per-SP file in `batch-data/`. Each agent reads only its own ~2–3k slice. This is enforced in Step 10 step 4–5.
- **Spawn prompts reference, don't embed** — the Continuation Prompt (writer-agent template) lives in `[Course]-Continuation-Prompt.md`. Spawn prompts pass the file path; agents read it with the Read tool. Only the DO NOT FABRICATE rule is embedded verbatim (it's short and critical). This keeps the orchestrator's per-batch spawn-prompt cost minimal.
- **One batch per session is the recommended workflow** — the resume mechanism makes this seamless. Each new session reads ~500 tokens of resume state instead of accumulating thousands of tokens of conversation history. Continuing in-session is fine for quick consecutive batches but not recommended for the bulk of a build.
- **Plain markdown only** — use `## Headings`, paragraphs, and bulleted lists. Do **not** use Obsidian callouts (`> [!info]`, `> [!note]`, `> [!todo]`, `> [!tip]`, etc.) anywhere in note templates or generated content. Decorative emojis (✅, ⚠️, etc.) should not appear in body text.
- **Cobalt Commentary as summary, not dump** — if a Cobalt Commentary section is appended post-build (from an extracted commentary file), each subtopic gets a synthesised **5–8 bullet summary** of recurring themes across the question parts tagged to that subtopic. Never dump verbatim per-part bullets into the vault note.

## Out of Scope

The following are **not part of the Project Hero vault build** and should not be required from the user. If they have them and want to use them, fold in; if not, proceed without:

- **House style / formatting reference pages** — Claude infers conventions from mark schemes via NLM
- **Smart Mark Guidelines** — only relevant later when writing mark schemes for the Cobalt CMS
- **Cobalt CMS exports** (Commentary, MS&G, ET&T) — only if enriching notes with existing CMS content; must be checked for accuracy first
