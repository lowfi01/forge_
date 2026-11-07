# Match the method to the work

Choose the requested outcome before choosing artifacts. Small edits need no design document,
comparison panel or visual. A task may cross kinds; keep one owner and one acceptance story.

| Work | Useful result | Evidence and stopping condition |
| --- | --- | --- |
| Spike / investigation | Answer, evidence, recommendation and remaining uncertainty | Use the [prototype playbook](../playbooks/prototype.md); bound one question, experiment and time/effort budget. Stop when answered or budget exhausted; an inconclusive/no-build result is valid. |
| Plan | Ordered outcomes, dependencies, risks and completion checks | Use [plan](../../plan/SKILL.md); verify prerequisites and identify decisions. Plan-only does not authorize implementation. |
| Design | Contract, important alternatives, failure/recovery and selected approach | Use [architect](../../architect/SKILL.md); walk through actual scenarios. A diagram is a design claim, not runtime proof. |
| Programming | A working change fitting its callers and existing project | Use the relevant feature/bug-fix playbook, language guidance and proportional tests; inspect the actual result. |
| Writing | Clear, supported material for the intended audience | Use [unslop](../../unslop/SKILL.md), and social-content only for social writing; verify claims, references and whether the document enables its intended decision. |
| Game development | Mechanic, playable experiment, system, UI or asset | Read [game development](game-development.md); distinguish correctness, experience and performance. |

Use [visuals](../../visuals/SKILL.md) when a picture resolves confusion or supports a decision.
The visual type follows the question. Do not make every task produce every artifact.

At closeout, keep project continuity in the project's existing progress log. Once configured,
[worklog](../../worklog/SKILL.md) records meaningful completed units in the private ticket/daily
store as the last tool action of the turn. A status lookup does not log itself. Subtasks report
to the lead; the lead records the combined outcome once. Reusable lessons belong to
[reflect](../../reflect/SKILL.md), not a second copy of the activity log.
