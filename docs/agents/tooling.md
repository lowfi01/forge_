# Forge tools and optional runtimes

Claude is the default host. Codex can use the same skills when requested.

| Tool | Purpose |
| --- | --- |
| `./install.sh` | Install skills and agents for Claude; rebuild repository mirrors |
| `./install.sh --codex` | Also install skill links for Codex in `~/.agents/skills` |
| `./install.sh --copy` | Copy skills and Claude agents instead of linking |
| `python3 scripts/check.py` | Validate names, descriptions, links, catalog and mirrors; flag retired skill references |

Codex agent presets live in `.codex/`; the installer does not install these globally.
Follow [model policy](model-policy.md) for the planner and builder configurations.

[Third-party notices](../../tools/THIRD_PARTY_NOTICES.md) and
[provenance](../../provenance.json) preserve source and license records.
Bundled references and examples do not install an external runtime or provider.
Check the tools available in the consuming project before using an optional renderer.
Static checks establish library consistency, not live model or application behavior.

For an authorized upstream update, compare the pinned source with the candidate,
adapt only the owning skills, and preserve attribution. Research records under
`tools/research/` are historical evidence, not additional active skills.
