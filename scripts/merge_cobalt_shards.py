#!/usr/bin/env python3
"""Merge per-section Cobalt commentary shards into the single spec-point-grouped
file research packs read (project.json -> paths.cobalt_content).

WHY A SCRIPT AND NOT AN AGENT (findings F22/F23/F28, 1PH0, July-August 2026):
- F22: thirteen extraction agents given one schema-free prompt produced two
  heading formats and three attribution formats. A merge keyed on qstnprt_ lost
  every shard that omitted the ids; a heading regex without optional backticks
  dropped two whole sections (162 of 659 entries) while the merged file still
  looked well-formed. This script parses the mandatory /hero-0-setup section-6
  schema, tolerates the known variants, and FAILS LOUDLY on anything that looks
  like an entry but does not parse -- silence is the failure mode being killed.
- F28: a crawl-order merge bled 63 subtopics' spec-point blocks under
  neighbouring subtopic headings (or under an agent's own "Method" notes),
  fabricating sibling-boundary disputes downstream. This script REBUILDS the
  subtopic layer from sp-mapping.json, so every spec-point block sits under its
  own subtopic by construction.
- F23: a shard corrected after the merge silently never reaches the merged
  file, and every count reconciliation passes on the stale output. --check
  exits non-zero when any shard is newer than the merged file; /hero-1-research
  runs it before anything reads paths.cobalt_content.
- F160 (2026-08-19): F23 one level up -- the check compared the merged file to
  the SHARDS but never to this SCRIPT, so a project merged under old code kept
  consuming its output while --check printed FRESH for twelve days (1PH0: 55
  subtopic headings missing from the merged file, an R1 then inferred "three
  consecutive empty headers" from the missing boundaries). --check now also
  fails when the script is newer than the merged file, and the merged header
  carries a SCHEMA_VERSION stamp so a schema mismatch is self-evident to both
  the check and a human reader. A merged file without the current stamp is
  STALE by definition.

Dedup key is (spec_point_id, kind, part_key) -- NEVER part alone and never
qstn alone: a part tagged to two spec points must appear under both headings,
so a naive dedup deletes correct content (F22).

Acceptance test (hard): parsed entries - duplicates dropped == entries emitted.

Usage:
  python merge_cobalt_shards.py <project_dir>                 # merge (finds shards
                                  recursively, e.g. in research/cobalt-commentary/)
  python merge_cobalt_shards.py <project_dir> --check         # staleness gate only
  python merge_cobalt_shards.py <project_dir> --shard-glob "*-Cobalt-Content-S*.md"
  python merge_cobalt_shards.py <project_dir> --mapping sp-mapping.json --output 1PH0-Cobalt-Content.md
"""
import argparse
import glob as globmod
import json
import os
import re
import sys

MARKER = "<!-- merge_cobalt_shards v1 -->"
# Bump on ANY change to the parse/emit schema (F160). --check fails a merged
# file whose header carries a different stamp, so the bump is what turns a
# script fix into a loud re-merge instead of a silent twelve-day drift.
SCHEMA_VERSION = "schema-v2"
EMPTY_SP_LINE = "_No commentary or Examiner Tips and Tricks found._"

KINDS = ("Commentary", "Examiner Tips and Tricks", "Unwrapped solution commentary")

# Tolerant of the variants F22 documented: optional backticks around the id.
SP_HEADING = re.compile(r"^####\s+(?P<name>.*?)\s*\(\s*`?(?P<id>spcpt_[A-Za-z0-9]+)`?\s*\)\s*$")
# Anything at #### level that mentions an spcpt but failed the parse above.
SP_HEADING_LOOSE = re.compile(r"^####.*spcpt_", re.I)

# **<kind>** -- qstn_x [part (b)] [-- qstnprt_y | no-part-id]
ENTRY = re.compile(
    r"^\*\*(?P<kind>" + "|".join(re.escape(k) for k in KINDS) + r")\*\*"
    r"\s*[—–-]+\s*(?P<qstn>qstn_[A-Za-z0-9]+)"
    r"(?:\s+part\s*\(?(?P<part>[A-Za-z0-9]+)\)?)?"
    r"(?:\s*[—–-]+\s*(?P<qstnprt>qstnprt_[A-Za-z0-9]+|no-part-id))?"
    r"\s*$"
)
ENTRY_LOOSE = re.compile(r"^\*\*(" + "|".join(re.escape(k) for k in KINDS) + r")\*\*")


def log(msg):
    print(msg, flush=True)


def sp_key(entry_dict, *keys):
    for k in keys:
        if entry_dict.get(k):
            return entry_dict[k]
    return None


def load_mapping(path):
    """sp-mapping.json -> ordered subtopic list + spcpt lookup.

    Handles both the fresh-build and build_mapping.py (legacy) key names."""
    data = json.load(open(path, encoding="utf-8"))
    subtopics = data.get("subtopics") or {}
    sp_names = {}       # spcpt_id -> name
    sp_subtopic = {}    # spcpt_id -> sbt_id
    for m in data.get("mapping") or []:
        spid = sp_key(m, "cobalt_sp_id", "sp_id", "id")
        if not spid:
            continue
        sp_names[spid] = sp_key(m, "cobalt_sp_name", "sp_name", "name") or spid
        sbt = sp_key(m, "cobalt_subtopic_id", "subtopic_id")
        if sbt:
            sp_subtopic[spid] = sbt
    # fall back to the subtopics dict for membership where mapping lacked it
    for sbt_id, sbt in subtopics.items():
        for spid in sbt.get("sp_ids", []):
            sp_subtopic.setdefault(spid, sbt_id)
    return subtopics, sp_names, sp_subtopic


def parse_shard(path):
    """Returns (entries, problems). entry = dict(sp_id, sp_name, kind, qstn,
    part, qstnprt, text, shard)."""
    entries, problems = [], []
    cur_sp = cur_sp_name = None
    cur_entry = None
    for i, raw in enumerate(open(path, encoding="utf-8").read().splitlines(), 1):
        line = raw.rstrip()
        m = SP_HEADING.match(line)
        if m:
            cur_sp, cur_sp_name, cur_entry = m.group("id"), m.group("name").strip(), None
            continue
        if SP_HEADING_LOOSE.match(line):
            problems.append(f"{os.path.basename(path)}:{i} spec-point-like heading did not parse: {line!r}")
            cur_sp = cur_sp_name = cur_entry = None
            continue
        if line.startswith("#"):        # any other heading ends the current block
            cur_entry = None
            if line.startswith("### "):  # shards must not emit the subtopic layer (F28)
                problems.append(f"{os.path.basename(path)}:{i} shard emits a '###' heading (schema forbids it -- a shard in this shape is in the pre-F28 schema and must be REGENERATED by re-running the stage-0 section-6 Cobalt commentary extraction; never hand-edit shards to fit): {line!r}")
            continue
        m = ENTRY.match(line)
        if m:
            if not cur_sp:
                problems.append(f"{os.path.basename(path)}:{i} entry outside any spec-point block: {line!r}")
                cur_entry = None
                continue
            cur_entry = {
                "sp_id": cur_sp, "sp_name": cur_sp_name,
                "kind": m.group("kind"), "qstn": m.group("qstn"),
                "part": m.group("part"), "qstnprt": m.group("qstnprt"),
                "text_lines": [], "shard": os.path.basename(path), "line": i,
            }
            entries.append(cur_entry)
            continue
        if ENTRY_LOOSE.match(line):
            problems.append(f"{os.path.basename(path)}:{i} entry-like line did not parse (check the em-dash separators and ids; if a shard fails wholesale, it is in a pre-current schema and must be REGENERATED via the stage-0 section-6 extraction, not hand-edited): {line!r}")
            cur_entry = None
            continue
        if cur_entry is not None:
            cur_entry["text_lines"].append(raw)
    for e in entries:
        e["text"] = "\n".join(e.pop("text_lines")).strip()
        if not e["text"]:
            problems.append(f"{e['shard']}:{e['line']} entry has an attribution header but no text ({e['kind']} {e['qstn']})")
    return entries, problems


def part_key(e):
    if e["qstnprt"] and e["qstnprt"] != "no-part-id":
        return e["qstnprt"]
    return f"{e['qstn']}:{e['part'] or ''}"


def norm_text(t):
    return re.sub(r"\s+", " ", t).strip().lower()


def main():
    ap = argparse.ArgumentParser(description="Merge Cobalt commentary shards (Project Hero, F22/F23/F28).")
    ap.add_argument("project_dir", help="project directory holding the shards and sp-mapping.json")
    ap.add_argument("--shard-glob", default="*-Cobalt-Content-S*.md")
    ap.add_argument("--mapping", default=None, help="path to sp-mapping.json (default: <project_dir>/sp-mapping.json)")
    ap.add_argument("--output", default=None, help="merged output path (default: derived from the shard prefix)")
    ap.add_argument("--check", action="store_true", help="staleness gate only: exit 1 if any shard is newer than the merged file")
    args = ap.parse_args()

    pdir = args.project_dir
    # The skill passes <project_dir>, but shards' natural home is
    # research/cobalt-commentary/ -- search recursively before concluding
    # nothing exists (2026-08-10 feedback: a flat glob here exited 2 on a
    # correctly laid-out project).
    shards = sorted(globmod.glob(os.path.join(pdir, args.shard_glob)))
    if not shards:
        shards = sorted(globmod.glob(os.path.join(pdir, "**", args.shard_glob), recursive=True))
    if not shards:
        log(f"No shards match {args.shard_glob!r} under {pdir} (searched recursively) -- nothing to merge.")
        log("(A single-agent extraction still writes a -S01 shard; the merged file is always produced by this script.)")
        sys.exit(2)
    shard_dirs = sorted({os.path.dirname(s) for s in shards})
    if len(shard_dirs) > 1:
        log(f"Shards found in {len(shard_dirs)} different directories -- move them together or narrow --shard-glob:")
        for d in shard_dirs:
            log("   " + d)
        sys.exit(2)

    # Derive the output name from the shard prefix unless given. A derived
    # output sits BESIDE the shards (not at project_dir) so a recursive find
    # keeps the merged file next to its sources.
    out = args.output
    if out and not os.path.isabs(out):
        out = os.path.join(pdir, out)
    if not out:
        prefixes = {re.sub(r"-S\d+\.md$", "", os.path.basename(s)) for s in shards}
        if len(prefixes) != 1:
            log(f"Shards carry {len(prefixes)} different prefixes ({sorted(prefixes)}) -- pass --output explicitly.")
            sys.exit(2)
        out = os.path.join(shard_dirs[0], prefixes.pop() + ".md")

    if args.check:
        if not os.path.exists(out):
            log(f"STALE: merged file does not exist yet: {out}")
            sys.exit(1)
        out_m = os.path.getmtime(out)
        newer = [s for s in shards if os.path.getmtime(s) > out_m]
        if newer:
            log(f"STALE (F23): {len(newer)} shard(s) newer than the merged file -- re-run the merge before anything reads paths.cobalt_content:")
            for s in newer:
                log("   " + os.path.basename(s))
            sys.exit(1)
        # F160: the merge SCRIPT itself is an input to the merged file. A merged
        # file older than the script may carry a retired schema (1PH0 ran twelve
        # days on one), so both legs below are STALE, not warnings.
        with open(out, encoding="utf-8") as f:
            head = f.read(2048)
        if SCHEMA_VERSION not in head:
            log(f"STALE (F160): merged file does not carry the current merge schema stamp ({SCHEMA_VERSION}) -- it was built by an older version of this script. Re-run the merge; if the merge then fails on shard-schema errors, the shards themselves are in an old schema and must be REGENERATED by re-running the stage-0 section-6 Cobalt commentary extraction.")
            sys.exit(1)
        if os.path.getmtime(os.path.abspath(__file__)) > out_m:
            log("STALE (F160): this merge script is newer than the merged file -- the file may be the output of retired code. Re-run the merge before anything reads paths.cobalt_content.")
            sys.exit(1)
        log(f"FRESH: merged file is newer than all {len(shards)} shard(s), carries the current {SCHEMA_VERSION} stamp, and post-dates the merge script.")
        sys.exit(0)

    mapping_path = args.mapping or os.path.join(pdir, "sp-mapping.json")
    if not os.path.exists(mapping_path):
        log(f"sp-mapping.json not found at {mapping_path} -- the subtopic layer is rebuilt from it (F28); cannot merge without it.")
        sys.exit(2)
    subtopics, sp_names, sp_subtopic = load_mapping(mapping_path)

    all_entries, all_problems, per_shard = [], [], {}
    for s in shards:
        entries, problems = parse_shard(s)
        per_shard[os.path.basename(s)] = len(entries)
        all_entries.extend(entries)
        all_problems.extend(problems)

    unknown = sorted({e["sp_id"] for e in all_entries} - set(sp_subtopic))
    if unknown:
        all_problems.append(f"{len(unknown)} spec-point id(s) in shards are not in sp-mapping.json: {unknown}")

    if all_problems:
        log("MERGE FAILED -- unparseable or unmappable content (fix the shard, do not hand-merge):")
        for p in all_problems:
            log("   " + p)
        sys.exit(1)

    # Dedup on (sp_id, kind, part_key) -- cross-tagged parts appear under BOTH
    # spec points, so sp_id stays in the key (F22).
    seen, dropped, conflicts, merged = {}, 0, [], []
    for e in all_entries:
        k = (e["sp_id"], e["kind"], part_key(e))
        if k in seen:
            if norm_text(seen[k]["text"]) == norm_text(e["text"]):
                dropped += 1
                continue
            conflicts.append(f"{k}: {seen[k]['shard']} vs {e['shard']} carry DIFFERENT text -- keeping both, reconcile at source")
        seen.setdefault(k, e)
        merged.append(e)

    by_sp = {}
    for e in merged:
        by_sp.setdefault(e["sp_id"], []).append(e)

    lines = [MARKER, "", f"# Cobalt commentary & Examiner Tips and Tricks -- merged by scripts/merge_cobalt_shards.py from {len(shards)} shard(s) ({SCHEMA_VERSION})", ""]
    emitted = 0
    for sbt_id, sbt in subtopics.items():
        sp_ids = sbt.get("sp_ids", [])
        if not any(sp in by_sp for sp in sp_ids):
            continue  # subtopic with no Cobalt content at all -- correctly absent
        lines.append(f"### {sbt.get('name', sbt_id)} ({sbt_id})")
        lines.append("")
        for spid in sp_ids:
            lines.append(f"#### {sp_names.get(spid, spid)} ({spid})")
            lines.append("")
            if spid not in by_sp:
                lines.append(EMPTY_SP_LINE)
                lines.append("")
                continue
            for e in by_sp[spid]:
                attribution = f"**{e['kind']}** — {e['qstn']}"
                if e["part"]:
                    attribution += f" part ({e['part']})"
                attribution += f" — {e['qstnprt'] or 'no-part-id'}"
                lines.append(attribution)
                lines.append(e["text"])
                lines.append("")
                emitted += 1

    # Acceptance test (F22): input - duplicates == output. Never write a file
    # that fails it.
    if len(all_entries) - dropped != emitted:
        log(f"MERGE FAILED reconciliation: parsed {len(all_entries)} - duplicates {dropped} != emitted {emitted}. Nothing written.")
        sys.exit(1)

    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines).rstrip() + "\n")

    log(f"Merged {len(shards)} shard(s) -> {out}")
    for name, n in per_shard.items():
        log(f"   {name}: {n} entries")
    log(f"RECONCILED: {len(all_entries)} parsed - {dropped} cross-shard duplicates = {emitted} emitted, "
        f"{len(by_sp)} spec points with content")
    if conflicts:
        log(f"\nWARNING -- {len(conflicts)} same-key entries with DIFFERENT text (both kept):")
        for c in conflicts:
            log("   " + c)
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
