# Forge

James's personal skill library for Claude Code by default, with Codex available when needed: one engineering method shared
across work, mobile apps, the trading bot, game dev and writing.

Forked from [Orbyn Fullstack Engineering Skills](https://github.com/kinqsradio/orbyn-fullstack-skills)
by Anh Dang (MIT), then initially pruned from 36 to 19 skills; now extended to 21, renamed, and set up for
cheap-by-default models. See [LICENSE](LICENSE) and [AUTHORS.md](AUTHORS.md).

*Herrero* is Spanish for blacksmith; this is where the tools get made.

## Install

```bash
./install.sh          # link skills and agents into ~/.claude (edits show up live)
./install.sh --copy   # copy instead of link
./install.sh --codex  # also link skills into ~/.agents/skills for Codex
```

Then open `claude` in any project and ask "what skills do you have?".
Re-run after adding or removing a skill. Check the library with
`python3 scripts/check.py`.

## Models

The main session runs on Sonnet. Two agents:

- `planner` (Opus): the plan before building, the review before merging, hard diagnosis.
- `builder` (Sonnet): implements from the plan; stops and asks when it hits a design decision.
- Fable: only when James picks it.

Details in [docs/agents/model-policy.md](docs/agents/model-policy.md).

## Skills

Full list with descriptions: [skills/README.md](skills/README.md).

| Area | Skills |
| --- | --- |
| Core method | `workflow`, `plan`, `how`, `why`, `interrogate`, `tdd` |
| Design and build | `architect`, `backend-design`, `data-migration`, `ai-application`, `stack-selection`, `research` |
| Delivery | `ci-design` |
| Mobile and UI | `ui-design` |
| Languages | `language-best-practices` |
| Writing and visuals | `unslop`, `social-content`, `visuals` |
| Memory and logs | `reflect`, `show-me-your-work`, `worklog` |

## Using it in a project

Add a `CLAUDE.md` at the project root with the facts the skills can't know:
stack and versions, how to run and test it, environments and how to reach them,
logs and dashboards, and conventions. Project-only skills go in the project's own
`.claude/skills/`.

## Roadmap

1. Rewrite the core around James's work: `dev-investigate`, `adversarial`, `pr-flow`, `oncall`.
2. Validate private `worklog` and `visuals` on real tasks; improve learning through `reflect`.
3. Domain packs: work (.NET, payroll), mobile, trading bot, Godot.
4. Keep routing limited to the maintained skills (`python3 scripts/check.py` checks the library).

## Pull upstream improvements

```bash
# upstream is already set in this repo; on a fresh clone add it with:
# git remote add upstream https://github.com/kinqsradio/orbyn-fullstack-skills.git
git fetch upstream
git diff upstream/main -- skills/interrogate   # paths differ for renamed skills
```

## How much process?

Use the smallest method that answers the request: a spike ends with evidence and a recommendation;
a design explains the contract and meaningful alternatives; code needs relevant checks; a game
needs separate correctness, experience and performance evidence. Visuals are conditional.
See [selected adaptations](docs/forge-adaptations.md) for the upstream source and what was omitted.
