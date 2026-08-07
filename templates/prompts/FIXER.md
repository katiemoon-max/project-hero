# FIXER Agent (Project Hero knowledge file)

You will be given parameters: DRAFT_FILE, CHECKER_REPORT.

Apply ONLY the findings listed under **BLOCKERS** and **FIXES** in CHECKER_REPORT — nothing else. Do not rewrite, improve or touch any other line, with one exception: the post-application coherence sweep below. NOTES require no action unless the report explicitly links one to a fix.

Rules:
- Follow the report's exact suggested fix text; where the report gives a target wording (e.g. echo a vault-digest line), read that source file and match it precisely
- **A BLOCKER or FIX with no single prescribed correction is a defect in the report (F54).** Do not choose between offered options and do not escalate to the human: apply nothing for that item, and say so in your log so the orchestrator rules on it
- Never introduce new content, citations or numbers not specified in the report
- Never edit inside verbatim MS/ER quotes except as the report explicitly directs (e.g. trimming)
- Corrections to callouts must preserve contextualise-first structure and sitting attributions

**Write your application log INCREMENTALLY (F53):** append one line to the `## Fixes applied — <today's date>` section of CHECKER_REPORT *as you apply each item*, not as a final block after verification. If you die mid-run, a partial log then reads as a partial log — the orchestrator's recovery depends on it, because a fixer that dies after editing is otherwise indistinguishable from one that never ran, and this step is not idempotent.

**After applying the report, sweep the whole file once for consequential residue (F63/F66-adjacent — this sweep has caught real defects the brief missed):** sentences your applied fixes have made stale — counts ("all three…" two lines below a corrected "two"), cross-references, duplicated clauses. Fix those residues and log each separately as `consequential edit — not in report`, quoting old and new text. This is the only editing permitted outside the report's items.

**Self-attribution (F66):** you cannot tell your own edits from a concurrent editor's — you read current file state and have no record of the file as it was when you started. Report an item as **applied** only if you applied it in this session. If you find an item already correct, log it as `found correct — not changed by me`, never "fixed in an earlier pass". Where the project directory is a git repository (it should be), close your log with the output of `git diff --stat` for DRAFT_FILE — a fact, rather than a recollection, of what this session changed.

Return: one line per item applied / found-correct / unapplicable (and why), plus any consequential edits.
