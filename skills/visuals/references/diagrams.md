# Diagrams and charts

Use Mermaid for compact sequence, flow and state diagrams. Use SVG/HTML when set overlap,
layout, annotations or interaction need more control. Use plotting tools for measurements.
A stack diagram shows relationships; a statechart shows transitions; do not mix their meanings.

Ground actors, components, labels and arrows in the design or observed source. Label an inferred
relationship. Separate runtime traffic from development/deployment dependencies through labels
and line style; do not rely on colour alone. Group by actual ownership/runtime boundaries.
For concurrency, show both sessions, the shared store, actual synchronization (including lock duration when applicable), conflict and retry.

Keep models and prose consistent. Give long or dense diagrams a readable text explanation or
table. Avoid mandatory themes, icon downloads or fixed geometry. Prefer generic pictograms;
use supplied/authorized brand assets when useful, preserve their provenance and visual identity.

Inspect the rendered view: arrow direction, line/label overlap, group membership, clipped text,
legends, units and contrast. A parser success does not prove layout or semantics. If rendering
is unavailable, deliver the source and explicitly leave visual inspection unverified.

Venn areas must not suggest measured proportions unless the construction actually represents
them. Prefer a comparison table when categories have no meaningful intersection. Charts must
retain units, sources, missing-data treatment and uncertainty; never invent numbers for a visual.
