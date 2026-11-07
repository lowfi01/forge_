# Worklog reference

## Session procedure

1. Log a real completed unit: decision, document change, ticket, PR, review, root cause, code change, or answered question. Skip trivial exchanges.
2. Resolve a canonical key and tier. Use tracker context when available; GitHub `org/repo#123` maps to `repo-123`. If different organizations have repositories with the same name, ask how to disambiguate. Ask if otherwise ambiguous. Keyless work is `BAU`.
3. For a ticket or epic, check out a unique copy, read it, edit the copy using the host's file tools, then commit. New-key checkouts have no content file yet: write the full file to the returned path. Update a parent epic after its ticket. An epic is a short rollup, not a duplicate ticket entry.
4. Append one daily block for the work. Always include What, Why, Outcome, and Next. Use full references and state whether work was prepared, attempted, failed, observed, or delivered. Record failures and unverified checks honestly. Never include secrets, connection strings, or customer data.
5. Take dates and times from the environment. Daily logs are local personal recall, not a shared system of record.

When updating ticket files, rewrite only the header above `## Session Log`; preserve all existing links and keep unresolved Open Questions word for word. Keep table rows in this order: Status, Current State, Epic (tickets only), Links. Put Open Questions below the table. Add the newest dated Session Log section above older ones, or append bullets to today's top section. Do not rewrite, reorder, or delete older entries. If old information was wrong, correct it in today's entry. Use 2–4 sentences for Current State. Ticket status is In Progress, Blocked, Done, or Superseded.

A ticket's Session Log bullet should state what changed, why, the full reference, and the reached stage. Epic log bullets name the child and summarize only its change. Keep epic `children` and Links current. A new ticket begins with `key: KEY` or a `# KEY: title` heading; an epic uses `key` and `children` frontmatter.

## Daily block shape

The script writes `### HH:MM · <KEY or BAU> · <type>[ · <session>]`. Types: `decision`, `PR review`, `PR`, `doc`, `ticket`, `root cause`, `question`, `investigation`, `fix`, `follow-up`.

Provide this body in a UTF-8 file written with the host's Write tool (Codex: use its UTF-8 file-write tool):

```markdown
**What:** Reviewed the freshness gate in example-org/billing-api#482; it checks mapped test-data age.
**Why:** Needed to determine whether the gate refreshes stale test data.
**Outcome:** It checks age only; under 3 days proceeds, 3–7 days offers refresh, and over 7 days blocks. Review delivered.
**Next:** TODO: verify whether refresh_map.py creates entries for tests with zero failures.
→ [repo-482](<../repo-482 - Freshness gate.md>)
```

Good Why: “Needed to determine whether the gate refreshes stale test data.” Bad Why: “Reviewed the freshness gate.” The bad version repeats What instead of explaining the reason. Keep each field to one or two sentences. `Next` is always present: `TODO: ...`, `waiting on ...`, or `none`. Omit the link for BAU. A correction later that day is a new `follow-up` block that identifies the earlier block.

## Commands

Quote paths containing spaces. All folder paths are absolute and already exist; scratch paths are absolute too. Write body text to a UTF-8 file; do not pipe it or use PowerShell `Set-Content`.

```text
python3 <skill>/scripts/worklog.py checkout --folder <F> --key PROJ-123 --to-dir <absolute-scratch>
python3 <skill>/scripts/worklog.py commit --folder <F> --key PROJ-123 --file <checkout-copy> [--name "PROJ-123 - Short summary.md"]
python3 <skill>/scripts/worklog.py append-daily --folder <F> --heading "PROJ-123 · PR review" [--session "review-2"] --body-file <UTF-8-body-file>
python3 <skill>/scripts/worklog.py begin --folder <F> [--key PROJ-123 --epic PROJ-100] --heading "PROJ-123 · fix" --body-file <UTF-8-body-file> [--session "session-a"]
python3 <skill>/scripts/worklog.py status --folder <F> [--operation <UUID>]
python3 <skill>/scripts/worklog.py commit --folder <F> --key PROJ-123 --file <checkout-copy> --operation <UUID> --stage ticket
python3 <skill>/scripts/worklog.py commit --folder <F> --key PROJ-100 --file <epic-checkout-copy> --operation <UUID> --stage epic
python3 <skill>/scripts/worklog.py append-daily --folder <F> --heading "PROJ-123 · fix" --body-file <UTF-8-body-file> --operation <UUID>
```

For a new key, commit requires `--name "PROJ-123 - Short summary.md"`; use only Windows-safe filename characters. The copy must contain a matching `key:` or `jira:` frontmatter line, or `# PROJ-123: title`. On an existing file commit checks that the target has not changed since checkout and that Session Log history is intact. On exit 6, discard the old edit, check out again, reread, redo the update, and commit the fresh copy. Never copy a base version from another checkout. `begin` freezes date, time, heading, session and body in `.operations/<UUID>.json`; `commit` stages must run ticket, epic, daily in order, omitting nonexistent stages. Pass the same UUID at every stage. If interrupted, inspect `status`, then retry a stage whose replace may have succeeded; embedded receipts make that retry exactly-once. Do not rollback completed stages. Status never appends to daily or updates ticket files.

### Examples

Existing ticket and epic: checkout `PROJ-123`, update and commit it, checkout `PROJ-100`, add one child rollup bullet and commit it, then append a single daily block for `PROJ-123`.

New key: checkout `PROJ-123`; write the complete ticket to the returned copy; commit with `--name "PROJ-123 - Replica endpoint.md"`; append the daily block.

BAU: write the body file and call `append-daily --heading "BAU · question"`. No ticket/epic file is created.

Operation recovery: call `begin` once; retain its UUID; commit ticket, epic, and daily stages in order. If a command reports an error after the target replacement may have happened, use `status --operation UUID`. Retry that same stage and copy to reconcile its receipt; then continue pending stages.

## Safety and concurrency

The script uses an OS-level exclusive lock only while reading or writing; a killed process releases it automatically. Do not put the folder on a network share or cloud-sync folder because those may not honor the same lock semantics. Commits use compare-and-swap against the locked target, atomic same-folder replacement, and history checks. Daily appends replace the complete day file atomically under the same guard. Existing symlinks and paths escaping the folder are refused. The script never prints file contents.

## Exit codes

| Exit | Meaning | Agent action |
| --- | --- | --- |
| 0 | Done | Continue; for staged operations continue in order. |
| 1 | Script crashed | Show the error; do not retry blindly. Check `status` if a replace could have completed. |
| 2 | Usage error, including Python “can't open file” | Fix the command. If the script is missing, stop and tell the user the skill is not installed; never edit worklog files directly. |
| 3 | Invalid input, encoding, key, folder, name, sidecar, duplicate match, or history edit | Fix the input. For multiple key matches, ask which file is the worklog. |
| 5 | Guard busy after 20 seconds | Retry once; if it fails again, tell the user and provide the intended text. |
| 6 | Commit conflict | Check out again, redo the edit on the new copy, and commit that copy. |

No install, cloud synchronization, or external publishing is performed by these commands.

## Ticket and epic file examples

Ticket files have matching frontmatter, a rewritten summary header and append-only dated history:

```markdown
---
key: PROJ-123
epic: PROJ-100
status: in-progress
last_updated: 2026-11-07
---

# PROJ-123: Expose a read-only replica endpoint

| Field | Value |
| --- | --- |
| Status | In Progress |
| Current State | Design agreed. API field added and PR prepared for review. |
| Epic | PROJ-100 |
| Links | [Tracker](https://tracker.example/PROJ-123) · Epic: PROJ-100 · example-org/billing-api#482 |

**Open Questions**
- None.

## Session Log

### 2026-11-07 — billing-api (feature/proj-123)
- Added the API field and prepared example-org/billing-api#482 for review; CI has not run.
```

Epic files use `children` instead of `epic`, omit the Epic table row, and summarize each child once:

```markdown
---
key: PROJ-100
children: [PROJ-123, PROJ-124]
status: in-progress
last_updated: 2026-11-07
---

# PROJ-100: Replica read path

| Field | Value |
| --- | --- |
| Status | In Progress |
| Current State | PROJ-123 added the API field and its PR is awaiting review. PROJ-124 is not started. |
| Links | PROJ-123 · PROJ-124 · [Design](https://docs.example/replica-read-path) |

**Open Questions**
- None.

## Session Log

### 2026-11-07
- PROJ-123: API field added; PR prepared for review ([PROJ-123](<./PROJ-123 - Replica endpoint.md>)).
```

Where-something-stands questions are read-only: inspect ticket/epic files or use `status`; do not create a worklog entry just for a status lookup.
