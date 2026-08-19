#!/usr/bin/env python3
"""Pack-freshness check for Project Hero session resume (Katie's ask, 19 Aug 2026).

WHY (Round 10/11 history): every freshness mechanism before this one compared a
project against its LOCAL pack clone -- pack_commit (F76), the /hero-2-write
prompts/scripts diff -- and none of them ever asked GitHub anything. So a clone
that was never pulled passes every check vacuously: on 18-19 Aug a course owner
held a wave at the publish gate for F159 a full day after F159 was fixed at
origin, because nothing in the process ever fetched. This script is the front
door /hero runs at every session resume:

  1. FETCH origin and compare HEAD to origin/main.
  2. RE-PULL automatically -- but only fast-forward on a clean tree. A dirty
     tree or a diverged branch BLOCKS the pull and says so loudly; this script
     must never eat a local change or create a merge commit on someone's clone.
  3. PROJECT REFRESH (--project): a pack pull updates NOTHING in a project --
     every brief resolves to the project's own prompts/scripts copies (the
     exact trap F76 documents). So after the pull, classify each project copy
     against the pack: differs + no PACK PROVENANCE header = STALE (refresh);
     differs + header = deliberate customisation (keep, always); differs + the
     pack knows it REIMPLEMENTED the file (RECONCILE_PENDING below) = RECONCILE,
     held for a human regardless of header. With --apply, stale copies are
     refreshed from the pack and project.json -> pack_commit is advanced -- but
     only once nothing stale remains.
  4. SKILLS REFRESH (--skills-dir): the installed Claude Code skill copies are
     assumed to be PURE PACK COPIES -- customisations belong in a project's
     prompts/, never in an installed skill. A differing skill file is refreshed
     under --apply, but never silently-and-totally (Leander, 19 Aug 2026): a
     PACK PROVENANCE header is respected exactly as in step 3, and any other
     modified file is backed up beside itself as <name>.pre-refresh-<head>
     before being overwritten, with the backup path printed.

Exit codes: 0 = current (or made current); 1 = action needed (blocked pull,
stale copies in report-only mode, or a customisation shadowing a pack change);
2 = could not check (not a git repo, no project.json where one was named).
Offline is NOT an error: a failed fetch warns and continues against the local
ref -- a session must be able to start on a train.

Usage:
  python pack_freshness.py                     # pack pull check only
  python pack_freshness.py --project <dir>     # + report the project's copies
  python pack_freshness.py --project <dir> --apply   # + refresh stale copies
  python pack_freshness.py --pack <dir>        # if auto-detection fails
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):  # Windows cp1252 guard (pack-wide gotcha)
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

PROVENANCE_MARKER = "PACK PROVENANCE"
PROVENANCE_SCAN_BYTES = 4096  # header convention: marker sits in the first lines

# Files the pack KNOWS it reimplemented rather than adopted (its own skill text
# says "reconcile with the course original when upstreamed"). A project copy of
# one of these that differs is a RECONCILE, never a STALE -- auto-overwriting it
# would resolve a held reconciliation by side effect (Leander, 19 Aug 2026: the
# 1PH0 rn_derived_sweep original survived only because a human read the diff and
# added a provenance header in time). Remove an entry when its reconciliation is
# ruled and the ledger says so.
RECONCILE_PENDING = frozenset({
    "scripts/rn_derived_sweep.py",   # hero-3-check: pack copy is a fresh implementation of F149's spec
})

# project dir -> pack dir mapping for the refresh classifier. Prompts come from
# templates/prompts/ (hero-0 setup act), scripts from scripts/.
COPY_MAP = (
    ("prompts", os.path.join("templates", "prompts")),
    ("scripts", "scripts"),
)


def log(msg=""):
    print(msg, flush=True)


def git(pack_dir, *args, timeout=120):
    r = subprocess.run(
        ["git", "-C", pack_dir, *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=timeout,
    )
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def find_pack_dir(cli_pack, project_dir):
    """Resolve the pack clone: --pack wins; then project.json paths.pack_dir;
    then this script's own location if it sits inside a project-hero clone."""
    if cli_pack:
        return os.path.abspath(cli_pack)
    if project_dir:
        pj = os.path.join(project_dir, "project.json")
        if os.path.exists(pj):
            try:
                with open(pj, encoding="utf-8") as f:
                    recorded = json.load(f).get("paths", {}).get("pack_dir")
                if recorded and os.path.isdir(recorded):
                    return os.path.abspath(recorded)
            except Exception:
                pass
    here = os.path.dirname(os.path.abspath(__file__))
    candidate = os.path.dirname(here)
    rc, out, _ = git(candidate, "remote", "get-url", "origin")
    if rc == 0 and "project-hero" in out:
        return candidate
    return None


def step1_pull(pack_dir):
    """Fetch + fast-forward. Returns (ok, old_head, new_head, pulled_subjects)."""
    rc, head, err = git(pack_dir, "rev-parse", "--short", "HEAD")
    if rc != 0:
        log(f"NOT A GIT REPO: {pack_dir} ({err})")
        sys.exit(2)

    log(f"Pack clone: {pack_dir} (HEAD {head})")
    try:
        rc, _, err = git(pack_dir, "fetch", "origin", timeout=90)
        offline = rc != 0
    except subprocess.TimeoutExpired:
        offline, err = True, "fetch timed out"
    if offline:
        log(f"WARNING: could not fetch origin ({err}) -- checking against the")
        log("last-known origin/main only. Freshness is NOT verified upstream.")

    rc, behind, _ = git(pack_dir, "rev-list", "--count", "HEAD..origin/main")
    rc2, ahead, _ = git(pack_dir, "rev-list", "--count", "origin/main..HEAD")
    behind, ahead = int(behind or 0), int(ahead or 0)

    if behind == 0:
        log("Pack is CURRENT with origin/main."
            + (" (unverified -- offline)" if offline else ""))
        return True, head, head, []

    _, subjects, _ = git(pack_dir, "log", "--format=%h %s", "HEAD..origin/main")
    pulled = subjects.splitlines()
    log(f"Pack is {behind} commit(s) BEHIND origin/main:")
    for line in pulled:
        log(f"  {line}")

    _, dirty, _ = git(pack_dir, "status", "--porcelain")
    if dirty:
        log("PULL BLOCKED -- the pack clone has local changes:")
        for line in dirty.splitlines():
            log(f"  {line}")
        log("Commit, stash or reconcile (PACK-DIVERGENCE.md) first, then re-run.")
        return False, head, head, pulled
    if ahead > 0:
        log(f"PULL BLOCKED -- the clone is also {ahead} commit(s) AHEAD of "
            "origin/main (diverged). Reconcile manually; this script never merges.")
        return False, head, head, pulled

    rc, _, err = git(pack_dir, "merge", "--ff-only", "origin/main")
    if rc != 0:
        log(f"PULL FAILED (ff-only refused): {err}")
        return False, head, head, pulled
    _, new_head, _ = git(pack_dir, "rev-parse", "--short", "HEAD")
    log(f"PULLED {head} -> {new_head} (fast-forward, {behind} commit(s)).")
    return True, head, new_head, pulled


PROVENANCE_LINE = re.compile(
    r"""^\s*(?:<!--\s*|\#\s*|//\s*|"{3}\s*|'{3}\s*)?PACK\ PROVENANCE\b""")


def has_provenance(path):
    """A provenance HEADER is a line beginning 'PACK PROVENANCE' in the first
    few lines (comment prefixes tolerated), per the convention
    spec_coverage_gate.py models. Never a raw substring scan: pack files
    legitimately MENTION the marker mid-sentence (the /hero skill documents
    the classifier itself), and a substring match classified the hero skill
    as a customisation in testing -- which would have exempted it from the
    very refresh it mandates."""
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            head = f.read(PROVENANCE_SCAN_BYTES)
    except OSError:
        return False
    return any(PROVENANCE_LINE.match(line) for line in head.splitlines()[:10])


def same_bytes(a, b):
    try:
        if os.path.getsize(a) != os.path.getsize(b):
            return False
        with open(a, "rb") as fa, open(b, "rb") as fb:
            return fa.read() == fb.read()
    except OSError:
        return False


def step2_project(pack_dir, project_dir, apply_fixes, pack_head):
    pj_path = os.path.join(project_dir, "project.json")
    if not os.path.exists(pj_path):
        log(f"NO project.json in {project_dir} -- nothing to refresh.")
        sys.exit(2)
    with open(pj_path, encoding="utf-8") as f:
        pj_text = f.read()
    try:
        pack_commit = json.loads(pj_text).get("pack_commit")
    except Exception:
        pack_commit = None
    log(f"\nProject: {project_dir}")
    log(f"  project.json pack_commit: {pack_commit or 'MISSING (F76 baseline absent)'}")

    if pack_commit:
        rc, _, _ = git(pack_dir, "cat-file", "-e", f"{pack_commit}^{{commit}}")
        if rc == 0:
            _, changed, _ = git(pack_dir, "diff", "--name-status",
                                f"{pack_commit}..HEAD", "--",
                                "skills", "scripts", "templates")
            if changed:
                log(f"  Pack changes since this project's baseline ({pack_commit}..{pack_head}):")
                for line in changed.splitlines():
                    log(f"    {line}")
            else:
                log("  No pack skills/scripts/templates changes since the baseline.")
        else:
            log(f"  WARNING: recorded pack_commit {pack_commit} is not in this clone.")

    stale, custom, shadowed, reconcile = [], [], [], []
    for proj_sub, pack_sub in COPY_MAP:
        proj_root = os.path.join(project_dir, proj_sub)
        pack_root = os.path.join(pack_dir, pack_sub)
        if not os.path.isdir(proj_root):
            continue
        for name in sorted(os.listdir(proj_root)):
            proj_file = os.path.join(proj_root, name)
            pack_file = os.path.join(pack_root, name)
            if not os.path.isfile(proj_file) or not os.path.exists(pack_file):
                continue  # course-specific files with no pack counterpart: theirs
            if same_bytes(proj_file, pack_file):
                continue
            if f"{proj_sub}/{name}" in RECONCILE_PENDING:
                reconcile.append(f"{proj_sub}/{name}")
                continue
            if has_provenance(proj_file):
                custom.append(f"{proj_sub}/{name}")
                # A customisation whose PACK original also moved since the
                # baseline needs a human look -- the local reasoning may predate
                # the pack change (the F153-F156 double-application trap).
                if pack_commit:
                    rc, _, _ = git(pack_dir, "diff", "--quiet",
                                   f"{pack_commit}..HEAD", "--",
                                   os.path.join(pack_sub, name).replace(os.sep, "/"))
                    if rc == 1:
                        shadowed.append(f"{proj_sub}/{name}")
            else:
                stale.append((f"{proj_sub}/{name}", pack_file, proj_file))

    if custom:
        log(f"  KEPT (PACK PROVENANCE customisations): {', '.join(custom)}")
    if reconcile:
        log("  RECONCILE -- the pack's copy is a known reimplementation of this")
        log("  project's original (see RECONCILE_PENDING); held for a human, never")
        log("  auto-overwritten. Reconcile the two, then remove the entry:")
        for name in reconcile:
            log(f"    {name}")
    if shadowed:
        log("  REVIEW NEEDED -- customised files whose pack original ALSO changed")
        log("  since the baseline (reconcile by hand, never auto-overwrite):")
        for name in shadowed:
            log(f"    {name}")
    if not stale:
        log("  No stale copies -- project prompts/scripts match the pack"
            " (customisations aside).")
        if apply_fixes and not shadowed and not reconcile:
            advance_pack_commit(pj_path, pj_text, pack_commit, pack_head)
        return 1 if (shadowed or reconcile) else 0

    log(f"  STALE copies ({len(stale)}) -- differ from pack, no provenance header:")
    for name, _, _ in stale:
        log(f"    {name}")
    if not apply_fixes:
        log("  Re-run with --apply to refresh these from the pack.")
        return 1
    for name, pack_file, proj_file in stale:
        shutil.copyfile(pack_file, proj_file)
        log(f"  REFRESHED {name}")
    if shadowed or reconcile:
        log("  pack_commit NOT advanced -- shadowed customisations or RECONCILE"
            " holds above need a human first.")
        return 1
    advance_pack_commit(pj_path, pj_text, pack_commit, pack_head)
    return 0


def step3_skills(pack_dir, skills_dir, apply_fixes, pack_head):
    """Installed-skills refresh (19 Aug 2026; hardened same day on Leander's
    verification note): the Claude Code skills directory holds a THIRD copy of
    the pack -- Step 1 of the setup guide copies skills/ into it, and nothing
    ever refreshed it (the reference machine's own hero-3-check was caught a
    wave of hardenings stale). ASSUMPTION, stated because it is load-bearing:
    installed skills are PURE PACK COPIES -- customisations belong in a
    project's prompts/, never in an installed skill. Because someone may
    hand-edit one anyway, the refresh is never silent-and-total: a PACK
    PROVENANCE header is respected (kept + flagged), and any other modified
    file is backed up beside itself before being overwritten."""
    pack_skills = os.path.join(pack_dir, "skills")
    stale, missing, custom = [], [], []
    for skill in sorted(os.listdir(pack_skills)):
        src_root = os.path.join(pack_skills, skill)
        if not os.path.isdir(src_root):
            continue
        dst_root = os.path.join(skills_dir, skill)
        if not os.path.isdir(dst_root):
            missing.append(skill)
            continue
        for base, _, names in os.walk(src_root):
            rel = os.path.relpath(base, src_root)
            for name in names:
                src = os.path.join(base, name)
                dst = os.path.join(dst_root, rel, name)
                label = f"{skill}/{name}" if rel == "." else f"{skill}/{rel}/{name}"
                if not os.path.exists(dst):
                    stale.append((label, src, dst, False))
                elif not same_bytes(src, dst):
                    if has_provenance(dst):
                        custom.append(label)
                    else:
                        stale.append((label, src, dst, True))
    log(f"\nInstalled skills: {skills_dir}")
    if missing:
        log(f"  NOT INSTALLED (copy from the pack's skills/): {', '.join(missing)}")
    if custom:
        log(f"  KEPT (PACK PROVENANCE header): {', '.join(custom)} -- note: a"
            " customised INSTALLED skill is unusual; customisations normally"
            " belong in the project's prompts/, so check this is deliberate")
    if not stale:
        log("  Installed hero skills match the pack"
            + (" (customisations aside)." if custom else "."))
        return 1 if (missing or custom) else 0
    log(f"  STALE installed skill files ({len(stale)}):")
    for label, _, _, _ in stale:
        log(f"    {label}")
    if not apply_fixes:
        log("  Re-run with --apply to refresh these from the pack.")
        return 1
    for label, src, dst, existed in stale:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if existed:  # never destroy a local edit silently -- back it up first
            backup = f"{dst}.pre-refresh-{pack_head}"
            shutil.copyfile(dst, backup)
            log(f"  REFRESHED {label} (previous version kept at {os.path.basename(backup)})")
        else:
            log(f"  REFRESHED {label} (was absent)")
        shutil.copyfile(src, dst)
    log("  Refreshed skills take effect from the next skill invocation.")
    return 1 if (missing or custom) else 0


def advance_pack_commit(pj_path, pj_text, old, new):
    """Targeted textual update -- project.json is hand-maintained; a json.dump
    round-trip would reformat the whole file."""
    if old == new:
        return
    new_text, n = re.subn(r'("pack_commit"\s*:\s*")[^"]*(")',
                          rf"\g<1>{new}\g<2>", pj_text, count=1)
    if n == 1:
        with open(pj_path, "w", encoding="utf-8", newline="") as f:
            f.write(new_text)
        log(f"  project.json pack_commit -> {new}")
    else:
        log(f"  WARNING: could not update pack_commit in project.json -- set it"
            f" to {new} by hand.")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pack", help="pack clone directory (auto-detected if omitted)")
    ap.add_argument("--project", help="project directory to check/refresh")
    ap.add_argument("--apply", action="store_true",
                    help="refresh stale project copies and advance pack_commit")
    ap.add_argument("--skills-dir",
                    help="Claude Code skills directory holding the installed"
                         " hero-* skill copies — refreshed to match the pack")
    args = ap.parse_args()

    pack_dir = find_pack_dir(args.pack, args.project)
    if not pack_dir:
        log("Could not locate the pack clone -- pass --pack <dir> (or record"
            " paths.pack_dir in project.json).")
        sys.exit(2)

    ok, _, new_head, _ = step1_pull(pack_dir)
    rc = 0 if ok else 1
    if not ok and (args.project or args.skills_dir):
        log("\nSkipping the copy refresh -- the pack pull is blocked, so a diff"
            " against this clone would be a diff against stale content.")
    elif ok:
        if args.project:
            rc = max(rc, step2_project(pack_dir, os.path.abspath(args.project),
                                       args.apply, new_head))
        if args.skills_dir:
            rc = max(rc, step3_skills(pack_dir, os.path.abspath(args.skills_dir),
                                      args.apply, new_head))
    sys.exit(rc)


if __name__ == "__main__":
    main()
