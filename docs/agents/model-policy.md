# Model policy

Plan and review with a strong model, build with a cheaper one. Structure, not
model size, keeps the code good: a concrete plan, a test that fails first, and a
strong-model review before merge.

| Agent | Claude | Codex | Use for |
| --- | --- | --- | --- |
| main session (default) | `sonnet` / medium | `gpt-6-luna` / high | everyday work |
| `builder` | `sonnet` / medium | `gpt-6-luna` / high | bounded implementation from a plan, small edits, lookups, docs, checks |
| `planner` | `opus` / medium | `gpt-6.1-sol` / medium | plans, design decisions, hard diagnosis, adversarial review |
| human-only | `fable` | `gpt-6-astra` | genuinely hard design questions, chosen by James only |

Rules:

- Call `planner` at two moments: before building (the plan) and before merging,
  presenting or going live (the review). Not on every edit.
- `builder` stops and reports when it needs a design decision the plan doesn't cover.
- Never escalate to the human-only tier automatically.
- Agents may not spawn further agents. At most two run at once.
- Long chats cost more than short ones: pause with a handoff and start fresh.

`models.json` is the record of these choices. Edit it, then update
`.claude/agents/*.md`, `.codex/agents/*.toml`, `.claude/settings.json` and
`.codex/config.toml` to match.
