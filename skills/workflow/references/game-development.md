# Game development evidence

Read the game's actual engine/version, scene or entity ownership, resource/asset rules,
input mapping, save format, target hardware and run/export commands. Do not impose Godot
on another engine. In Godot projects inspect scene lifecycle, signal connections and resource
sharing before changing them; use the project's installed-version documentation when needed.

Start a mechanic spike with one question, such as whether the grapple remains controllable
through a direction change. Build the smallest playable experiment with disposable data.
Do not turn a feel experiment into a complete production architecture.

Keep three evidence categories separate:
- Correctness: state transitions, damage/inventory rules, save/load compatibility, input and pause handling.
- Experience: responsiveness, readability, teaching, pacing and enjoyment. Agent interaction is preliminary evidence; human playtesting owns claims about fun.
- Performance: measured frame time, memory and loading on named hardware/build settings. A desktop editor run does not qualify a mobile export.

Use enemy statecharts, progression flowcharts, combat timing plots, level sketches or animation
studies only for the decision they explain. Concept art and simulated animations are proposals;
actual engine capture is implementation evidence. Keep source assets editable, record origin and
usage rights, and include reduced-motion/accessibility considerations where applicable.

A change completes when its agreed technical checks and available playtest checks are reported,
with untested hardware and unresolved experience questions explicit. Do not require a full game
playthrough or new harness for an isolated low-risk change.
