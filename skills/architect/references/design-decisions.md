# A small design record

Use an existing design/spec/plan document. If durable handoff is useful and none exists,
put one record in the project's normal location (otherwise `docs/work/<task>.md`). A small
settled change can stay in chat. Do not create separate plan, decision and design stores.

Record only what affects implementation or later decisions:
1. Problem, audience/caller, desired outcome and exclusions.
2. Observed constraints and unknowns; distinguish evidence from assumptions.
3. Proposed contract, owners, important data and failure/recovery paths.
4. Alternatives only for a real unresolved choice. Start with at most two, including the
   simpler/no-change option when viable. Compare the same inputs and hard constraints;
   inspect the actual sketches and select one coherent approach. No mandatory model panel.
5. Useful diagrams and what they establish: intended design, simulation, checked model or
   observed implementation. Keep labels and models consistent with the written contract.
6. Ordered implementation units, acceptance checks, rollback/recovery and unresolved decisions.

Stop comparing when evidence selects a choice. If neither meets a hard constraint, say so.
A spike can end inconclusively at its agreed limit. Preserve the reason a rejected alternative
was rejected only if it can prevent a future repeated decision.

Validate by walking through normal use, one meaningful failure and relevant concurrency,
compatibility or interruption scenarios. Use tests or a small experiment where reasoning alone
cannot settle the uncertainty. A rendered chart is not a successful runtime test.
