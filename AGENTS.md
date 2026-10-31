# Library instructions

James's personal skill library for Claude Code and Codex: engineering method for
work (payroll, .NET), mobile apps, a trading bot, game dev and writing.

Forked from the MIT-licensed Orbyn Fullstack Engineering Skills by Anh Dang
(https://github.com/kinqsradio/orbyn-fullstack-skills), then pruned and renamed.
Keep `LICENSE`, `AUTHORS.md`, `provenance.json` and `tools/` attribution intact.

## Layout

- `skills/<name>/SKILL.md`: one skill per folder; `references/`, `examples/` and
  `playbooks/` load only when the skill links to them.
- `.claude/skills` and `.agents/skills`: symlink mirrors of `skills/`.
- `.claude/agents/`, `.codex/agents/`: `planner` (strong model) and `builder` (cheap model).
- `docs/agents/model-policy.md`: which model when.
- `install.sh`: links skills and agents into `~/.claude`.
- `scripts/check.py`: validates names, descriptions, links and mirrors.

## Editing rules

- Folder name, `name:` field and catalog entry must match.
- Descriptions say when to use the skill, in one line, under 1024 characters.
- Keep SKILL.md short; move detail to a linked reference file.
- Links between skills stay inside `skills/` so installed copies still resolve.
- Run `python3 scripts/check.py` after any change.
- Prefer editing an existing skill over adding a new one. Cut skills unused for a month.
