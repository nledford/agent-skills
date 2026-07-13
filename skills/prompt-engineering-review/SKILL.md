---
name: prompt-engineering-review
description: Review and improve prompts for Codex, OpenCode, Weave, Claude, and other coding agents. Use for prompt audits, rewrites, acceptance criteria, and agent instruction quality; do not use for application implementation or reusable SKILL.md authoring.
---

# Prompt Engineering Review Skill

Use this skill to review or rewrite a task prompt, system prompt, agent role, or
delegation instruction. Use
[`create-agent-skill`](../create-agent-skill/SKILL.md) instead when creating or
maintaining a reusable `SKILL.md` contract.

Before reporting prompt findings, apply
[`review-verification-protocol`](../review-verification-protocol/SKILL.md) so
each issue is anchored in the actual prompt and tied to likely agent behavior.

Do not use it to implement the task described by the prompt unless the user also
requests implementation.

## Workflow

1. Identify the intended agent, objective, inputs, scope, non-goals,
   deliverables, autonomy, and success criteria.
2. Find ambiguity, contradiction, missing context, unsafe authority, and
   instructions that cannot be verified.
3. Add sequencing only where order matters, and require repository or external
   evidence instead of invented context.
4. Specify editing boundaries, testing expectations, acceptance criteria,
   failure reporting, and escalation conditions when relevant.
5. Remove duplicated policy and unnecessary verbosity. Preserve the user's
   intent and state assumptions that remain unresolved.
6. Match the deliverable to the request: review-only prompts need findings;
   rewrite or optimization requests need a replacement prompt.

## Output

For review-only requests, report prioritized findings first, their likely effect
on agent behavior, and unresolved assumptions. A replacement prompt is optional
unless requested. For rewrite or optimization requests, provide the replacement
Markdown prompt alongside the findings and assumptions.
