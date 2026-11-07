#!/usr/bin/env python3
"""Validate the skill library: names, descriptions, links, catalog and mirrors."""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = os.path.join(ROOT, "skills")
errors, warnings = [], []
LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)\s#]+)(?:#[^)]*)?\)")

names = sorted(d for d in os.listdir(SKILLS) if os.path.isdir(os.path.join(SKILLS, d)))
for n in names:
    p = os.path.join(SKILLS, n, "SKILL.md")
    if not os.path.exists(p):
        errors.append(f"{n}: missing SKILL.md"); continue
    head = open(p, encoding="utf-8").read().split("---")
    fm = head[1] if len(head) > 2 else ""
    m = re.search(r"^name:\s*(\S+)", fm, re.M)
    if not m or m.group(1) != n:
        errors.append(f"{n}: name field does not match folder")
    d = re.search(r"^description:\s*(.+)$", fm, re.M)
    if not d or not d.group(1).strip('" '):
        errors.append(f"{n}: missing description")
    elif len(d.group(1)) > 1024:
        errors.append(f"{n}: description over 1024 characters")

for dp, dirs, fs in os.walk(ROOT):
    # Generated output and preserved installer backups are not active library sources.
    if dp == ROOT:
        dirs[:] = [d for d in dirs if d not in (".git", "output", "upstream-references", "openSrc")]
    for f in fs:
        if not f.endswith(".md"): continue
        path = os.path.join(dp, f)
        for target in LINK.findall(open(path, encoding="utf-8").read()):
            if re.match(r"^[a-z]+:", target): continue
            full = os.path.normpath(os.path.join(dp, target))
            rel = os.path.relpath(path, ROOT)
            if not os.path.exists(full):
                errors.append(f"broken link {rel} -> {target}")
            elif rel.startswith("skills/") and not full.startswith(SKILLS):
                errors.append(f"link leaves skills/ (breaks when installed): {rel} -> {target}")

cat = json.load(open(os.path.join(SKILLS, "catalog.json")))
listed = {s["name"] for s in cat["skills"]}
for n in set(names) ^ listed:
    errors.append(f"catalog mismatch: {n}")

for mirror in (".claude/skills", ".agents/skills"):
    md = os.path.join(ROOT, mirror)
    have = set(os.listdir(md)) if os.path.isdir(md) else set()
    for n in set(names) - have: errors.append(f"{mirror}: missing link for {n}")
    for n in have - set(names): errors.append(f"{mirror}: stale link {n}")
    for n in have:
        entry = os.path.join(md, n)
        if not os.path.islink(entry):
            errors.append(f"{mirror}/{n}: expected a skill symlink; run install.sh")
        elif not os.path.exists(entry):
            errors.append(f"{mirror}/{n}: dangling symlink")
        elif os.path.realpath(entry) != os.path.realpath(os.path.join(SKILLS, n)):
            errors.append(f"{mirror}/{n}: link points to the wrong skill")

retired = ["orbyn-setup", "orbyn-worktree", "orbyn-skill-creator", "orbyn-upstream-review",
           "orbyn-content-design", "orbyn-security", "technical-illustration", "social-preview",
           "figure-it-out", "automate-me", "arena", "reverse-engineer-anything"]
for n in names:
    t = open(os.path.join(SKILLS, n, "SKILL.md"), encoding="utf-8").read()
    hits = [r for r in retired if re.search(rf"\b{re.escape(r)}\b", t)]
    if hits: warnings.append(f"{n}/SKILL.md mentions removed skills: {', '.join(hits)}")

for w in warnings: print("warn:", w)
for e in errors: print("ERROR:", e)
print(f"{len(names)} skills, {len(errors)} errors, {len(warnings)} warnings")
sys.exit(1 if errors else 0)
