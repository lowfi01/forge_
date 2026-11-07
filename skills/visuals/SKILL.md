---
name: visuals
description: "Explain or inspect a system, design, comparison or behaviour with diagrams, charts, illustrations or conditional interactive animation/video. Use when visual evidence helps a decision or the user requests a visual; skip decoration for routine edits."
---

# Choose the smallest useful visual

State what the reader should understand, the source evidence, audience and intended output.
Use the current project's visual language, assets and available tools. Do not build a new
rendering framework or install a provider simply to make a figure.

| Question | Starting format |
| --- | --- |
| Who sends what, and when? | Mermaid sequence diagram |
| Which decision leads where? | Mermaid flowchart |
| Which states and recovery paths are possible? | State diagram; [architect](../architect/SKILL.md) owns semantics |
| How do components connect? | Mermaid or SVG architecture diagram with labelled groups/edges |
| Which responsibilities overlap? | Labelled SVG Venn diagram, only for meaningful set overlap |
| What do measurements show? | Project plotting tools; real data, units and uncertainty |
| What should a concept look like? | Editable illustration or generated image using available tools |
| How does behaviour unfold or respond to input? | Small interactive HTML example or animation |
| What must be watched or shared as a demonstration? | Video when requested or materially useful |

Read [diagrams](references/diagrams.md) for precise charts, [images and motion](references/images-and-motion.md)
for artwork, interaction or video, and [review](references/review.md) before delivery.
For product UI itself use [ui-design](../ui-design/SKILL.md); for writing a design record use
[design decisions](../architect/references/design-decisions.md). An illustration does not change
or qualify the product it depicts.

Keep one editable source of truth and derive exports from it. Distinguish a proposal, a
simulation and observed implementation. Technical labels, edges and data stay in editable
code/vector sources even when generated art supplies a background or metaphor. Mark omitted
paths and limits. Do not imply measured results through attractive animation.

Deliver the viewable output plus its source when useful, with the actual render/interaction
checks and remaining limits. No automatic publishing or remote upload follows.
