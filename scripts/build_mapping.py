# Build the vault-SP -> Cobalt-structure mapping for a Project Hero export.
# Inputs:  Cobalt getCourseStructure dump (indented text) + vault SP note frontmatter
# Outputs: sp-mapping.json (machine map) + mapping-report.md (human mismatch report)
#
# Usage:
#   python build_mapping.py <structure-dump.txt> --vault-dir <spec-notes-dir> --out-dir <export-dir> [--aliases <aliases.json>]
#
# aliases.json (optional): {"<normalised vault sp name>": "<normalised cobalt sp name>", ...}
# for genuine name differences between vault and Cobalt (Cobalt names are authoritative).
import argparse
import json
import re
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("structure_file", type=Path)
parser.add_argument("--vault-dir", type=Path, required=True)
parser.add_argument("--out-dir", type=Path, required=True)
parser.add_argument("--aliases", type=Path, default=None)
args = parser.parse_args()

STRUCTURE_FILE = args.structure_file
VAULT_DIR = args.vault_dir
OUT_DIR = args.out_dir


def norm(s):
    s = s.replace("’", "'").replace("‘", "'")
    return re.sub(r"\s+", " ", s.strip().lower())


# vault spec_point name -> Cobalt SP name, for genuine name differences
ALIASES = {}
if args.aliases and args.aliases.exists():
    ALIASES = {norm(k): norm(v) for k, v in json.loads(args.aliases.read_text(encoding="utf-8")).items()}

# ---- 1. Parse the Cobalt structure dump ----
section = topic = subtopic = None
cobalt_sps = []          # list of dicts
subtopics = {}           # sbt_id -> {name, section, topic, sp_ids: []}
for line in STRUCTURE_FILE.read_text(encoding="utf-8").splitlines():
    m = re.match(r"^\s*(=*)\s*(\w+)\s*\|\s*(\S+)\s*(?:\|\s*(.*))?$", line)
    if not m:
        continue
    kind, _id, name = m.group(2), m.group(3), (m.group(4) or "").strip()
    if kind == "SECTION":
        section = {"id": _id, "name": name}
    elif kind == "TOPIC":
        topic = {"id": _id, "name": name}
    elif kind == "SUBTOPIC":
        subtopic = {"id": _id, "name": name, "section": section["name"], "topic": topic["name"], "sp_ids": []}
        subtopics[_id] = subtopic
    elif kind == "SPEC_POINT":
        sp = {"id": _id, "name": name,
              "section": section["name"], "topic": topic["name"],
              "subtopic_id": subtopic["id"], "subtopic": subtopic["name"]}
        cobalt_sps.append(sp)
        subtopic["sp_ids"].append(_id)

# ---- 2. Parse vault SP note frontmatter ----
def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        return None
    fm = {}
    for line in m.group(1).splitlines():
        km = re.match(r"^(\w+):\s*(.*)$", line)
        if km:
            v = km.group(2).strip().strip('"')
            fm[km.group(1)] = v
    return fm


vault_notes = []
for f in sorted(VAULT_DIR.glob("*.md")):
    if not re.match(r"^\d", f.name):
        continue  # skip Course Structure / Continuation Prompt / _RESUME etc.
    fm = frontmatter(f)
    if not fm or "spec_point" not in fm:
        continue
    vault_notes.append({"file": f.name, **{k: fm.get(k) for k in
                        ("number", "spec_point", "section", "topic", "subtopic", "unit", "level", "paper")}})

# ---- 3. Match vault notes to Cobalt SPs ----
# Primary key: (section, topic, sp name); fallback: sp name only if globally unique
by_key = {}
by_name = {}
for sp in cobalt_sps:
    by_key.setdefault((norm(sp["section"]), norm(sp["topic"]), norm(sp["name"])), []).append(sp)
    by_name.setdefault(norm(sp["name"]), []).append(sp)

mapping, mismatches, ambiguous = [], [], []
matched_cobalt_ids = set()
for note in vault_notes:
    sp_name = norm(note["spec_point"])
    sp_name = ALIASES.get(sp_name, sp_name)
    key = (norm(note["section"] or ""), norm(note["topic"] or ""), sp_name)
    cands = by_key.get(key, [])
    how = "section+topic+name"
    if not cands:
        cands = by_name.get(sp_name, [])
        how = "name-only"
    if len(cands) == 1:
        sp = cands[0]
        matched_cobalt_ids.add(sp["id"])
        mapping.append({"vault_file": note["file"], "vault_number": note["number"],
                        "vault_subtopic": note["subtopic"], "unit": note["unit"],
                        "match_how": how,
                        "cobalt_sp_id": sp["id"], "cobalt_sp_name": sp["name"],
                        "cobalt_subtopic_id": sp["subtopic_id"], "cobalt_subtopic": sp["subtopic"],
                        "cobalt_topic": sp["topic"], "cobalt_section": sp["section"]})
    elif len(cands) > 1:
        ambiguous.append({"note": note, "candidates": [(c["id"], c["section"], c["topic"], c["subtopic"]) for c in cands]})
    else:
        mismatches.append(note)

unmatched_cobalt = [sp for sp in cobalt_sps if sp["id"] not in matched_cobalt_ids]

# ---- 4. Write outputs ----
OUT_DIR.mkdir(parents=True, exist_ok=True)
(OUT_DIR / "sp-mapping.json").write_text(
    json.dumps({"mapping": mapping, "subtopics": subtopics}, indent=1, ensure_ascii=False), encoding="utf-8")

rep = []
rep.append("# Vault ↔ Cobalt mapping report\n")
rep.append(f"- Cobalt spec points: **{len(cobalt_sps)}** across **{len(subtopics)}** subtopics")
rep.append(f"- Vault SP notes: **{len(vault_notes)}**")
rep.append(f"- Matched: **{len(mapping)}** ({sum(1 for m in mapping if m['match_how']=='name-only')} via name-only fallback)")
rep.append(f"- Vault notes with NO Cobalt match: **{len(mismatches)}**")
rep.append(f"- Ambiguous matches: **{len(ambiguous)}**")
rep.append(f"- Cobalt SPs with no vault note: **{len(unmatched_cobalt)}**\n")
if mismatches:
    rep.append("## Vault notes with no Cobalt match\n")
    rep.append("| Vault file | Vault section | Vault topic |")
    rep.append("|---|---|---|")
    for n in mismatches:
        rep.append(f"| {n['file']} | {n['section']} | {n['topic']} |")
    rep.append("")
if ambiguous:
    rep.append("## Ambiguous matches\n")
    for a in ambiguous:
        rep.append(f"- **{a['note']['file']}** -> {a['candidates']}")
    rep.append("")
if unmatched_cobalt:
    rep.append("## Cobalt SPs with no vault note\n")
    rep.append("| Cobalt SP | Section | Topic | Subtopic |")
    rep.append("|---|---|---|---|")
    for sp in unmatched_cobalt:
        rep.append(f"| {sp['name']} | {sp['section']} | {sp['topic']} | {sp['subtopic']} |")
    rep.append("")
# subtopic grouping summary
multi = [s for s in subtopics.values() if len(s["sp_ids"]) > 1]
rep.append(f"\n## Subtopic grouping\n\n{len(subtopics)} Cobalt subtopics; {len(multi)} contain more than one SP.")
(OUT_DIR / "mapping-report.md").write_text("\n".join(rep), encoding="utf-8")
print(f"Cobalt SPs {len(cobalt_sps)} | vault notes {len(vault_notes)} | matched {len(mapping)} | "
      f"no-match {len(mismatches)} | ambiguous {len(ambiguous)} | cobalt-unmatched {len(unmatched_cobalt)}")
