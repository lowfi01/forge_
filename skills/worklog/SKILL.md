---
name: worklog
description: "Use when a real unit of work wraps up (decision, doc change, PR, review, root cause, sub-ticket, or answered question), when the user asks to update/log/save the worklog under any name or spelling, or asks where work stands. Personal recall, local only."
model: sonnet
---

> **Claude Code model caveat:** a skill's `model:` override applies for the rest of the current turn. If this skill fires during an Opus turn, later work in that turn also runs on Sonnet. Make worklog writes the last action of a turn.

Use the worklog for durable per-ticket/epic memory and a daily record. The folder comes from the user's private configuration; never guess or hard-code it. If no folder is configured, ask once. It must be a local folder on one machine, not a cloud-synced/shared folder: the OS lock coordinates only processes on that machine.

Before the first write in a session, read [the reference](references/daily-log.md). Use only `scripts/worklog.py` to write files. Log completed meaningful work without waiting to be asked; do not log trivial exchanges. Resolve a canonical key/tier from the conversation and tracker when available. GitHub `org/repo#123` becomes `repo-123`. If ambiguous, ask; if there is no key, use `BAU` for the daily entry.

For ticket/epic updates: checkout to an absolute scratch directory, read and edit the copy with the host's file tools, then commit. For a new key, checkout creates the sidecar but not the copy content; write the complete file to that returned path. A conflict (exit 6) means checkout again and redo on the fresh copy. Update ticket first, then its epic rollup. Always append one daily block per unit of work, including keyless work; the epic rollup does not get another daily block.

For the normal worklog update, prepare the daily body first, then use `begin` once and follow its frozen operation record: commit the ticket stage, then epic, then append daily with the same operation UUID. For BAU, begin with no key and complete its daily stage. The direct `checkout`/`commit` and `append-daily` commands remain available for low-level single-file work. `status` is read-only and reports stages inferred from embedded receipts. Re-submit the same stage to reconcile a write that succeeded just before a crash. Never undo a successful stage. See the reference for exact commands, formats, retry actions, and examples.
