# Codex Cowork Log — Forge

## Snapshot
- **Version:** 0.2.0
- **Last updated:** 2026-11-07
- **Stack:** Markdown skills, Python validator, shell installer; Claude and Codex presets.
- **Run:** `python3 scripts/check.py`; install with `./install.sh`, optionally `--codex`.
- **Working today:** 21 shared skills installed for Claude and Codex; worklog runtime suite passes on macOS.
- **Current focus:** Use the new skills on real work; Windows runtime qualification remains pending.

**Code map**
- `skills/workflow/SKILL.md` — routes tasks and delivery.
- `skills/plan/SKILL.md` — planning and task briefs.
- `skills/catalog.json` — discovery catalog.
- `docs/agents/model-policy.md` — planner/builder policy.
- `install.sh` — installation and discovery mirrors.
- `scripts/check.py` — static library validation.

## Progress index
| Versions | Dates | What we built | IDs closed | Where |
|---|---|---|---|---|
| 0.1.0 | 2026-11-07 | Recorded existing 19-skill baseline; cleaned retired workflow routes | T-001 | log |
| 0.2.0 | 2026-11-07 | Added worklog and visuals; task/design/game/learning guidance and verified installation | T-002, T-003, T-004, T-005 | log |

## TODO
### Now
- [ ] **T-006** Run worklog tests on Windows/NTFS; macOS results do not establish Windows behaviour.
- [ ] **T-007** Evaluate visuals and worklog on real Claude/Codex tasks; foundation routing review was read-based.
### Next
- [x] **T-003** Installed and byte-verified global Claude/Codex skill links. (v0.2.0)
### Later
- Domain packs and other roadmap items remain in README.md.
### Done (recent)
- [x] **T-004** Implemented worklog; 10 grouped runtime tests pass on macOS. (v0.2.0)
- [x] **T-005** Integrated visuals and task/design/learning guidance, repaired mirrors, completed bounded independent review. (v0.2.0)
- [x] **T-002** Reviewed extension and selected bounded upstream adaptations.
- [x] **T-001** Replace retired skill routes and stale tooling guidance; preserve attribution. (v0.1.0)

## Known issues
- **B-002** Windows execution and live Claude behaviour are unverified; Claude CLI was not logged in. User authorized Codex design/review for this build.

## Decisions
- **D-001** (2026-11-07) Claude is the default host; retain Codex compatibility when needed.
- **D-002** (2026-11-07) Retain upstream attribution, licenses, provenance and historical examples; remove obsolete operational dependencies.

## Changelog
### 0.2.0 — 2026-11-07
- Added task-kind, game-development, concise design-record and visual-selection guidance.
- Added visuals; worklog writer/docs are being implemented with history and recovery checks.
- Independent foundation read-review completed; installer executable/backup scanning fixes applied.
- User authorized Codex design/review instead of unavailable Opus and requested a new Developer/worklog data folder.
- Final macOS verification: 10 grouped runtime tests pass (150 daily appends, 64 concurrent commits, negative control, encoding, history, replay and injected failure checks); 21 skills, 0 errors, 0 warnings.
- Independent bounded review fixes verified: midnight recovery, first new-day history, same-key epic rejection, lock-directory symlink rejection and filename controls.
- Repaired placeholder mirrors with retained backups; installed/byte-verified both hosts and configured the private worklog outside Forge.
- Windows and live Claude execution remain unverified; rendered-media qualification is task-specific.
- Done: T-003, T-004, T-005 · Added: T-006, T-007.
- Publication requested: prepare a feature-branch commit and PR; remote delivery receipt belongs in the private daily log.

### 0.1.0 — 2026-11-07
- Created the progress log for the existing Forge library.
- Replaced routes to removed skills with maintained skills or direct guidance.
- Updated tool documentation to match the actual installer and validator.
- Preserved existing local changes and host model presets.
- Validation: 19 skills, 0 errors, 0 warnings; changed-file whitespace check passed.
- Whole-repository diff checking was blocked by host access to existing discovery mirrors; checks were scoped to the changed files.
- Done: T-001 · Added: T-002, T-003, B-001 · Decided: D-001, D-002.

## Notes for Codex
- Keep Claude as the default host; do not install or change host settings as part of documentation cleanup.
