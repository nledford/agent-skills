---
name: prompt-engineering-review
description: Review and improve prompts and bounded agent-system instruction interfaces for Codex, OpenCode, Weave, Claude, and other coding agents. Use for prompt audits, rewrites, multi-agent roles, delegation and handoff contracts, acceptance criteria, and quality gates; do not use for application implementation, runtime architecture audits, or reusable SKILL.md authoring.
---

# Prompt Engineering Review Skill

Use this skill to review or rewrite a task prompt, system prompt, agent role,
delegation instruction, or bounded interaction among agent instructions. Use
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

## Agent-System Review

Apply this method only when the assignment explicitly names two or more
interacting prompt artifacts, roles, or commands, or one orchestrator and its
named handoff contracts. Do not infer a repository-wide review from a single
prompt that merely mentions another agent.

1. Inventory the entry point, nodes, handoff edges, and state owners in the
   bounded interaction surface. Mark adjacent definitions as evidence rather
   than rewrite targets unless the request explicitly includes them.
2. Verify node and edge names, command ownership, tools, permissions, and
   lifecycle assumptions against supplied or repository evidence.
3. Check that authority, context, approvals, identity, and mutable-state
   ownership do not transfer implicitly across prompts, commands, skills, or
   delegation.
4. Check that every handoff is self-contained and that the receiver can consume
   its inputs and outputs without hidden state or invented context.
5. Compare start, progress, blocked, approval, retry, replay, escalation,
   reconciliation, and terminal semantics across participants. Identify loops,
   unreachable owners, and conflicting stop conditions.
6. Distinguish instruction defects from application architecture, runtime
   coordination, security-control correctness, test strategy, and release
   readiness; route those concerns to their owning review methods.
7. Separate static instruction evidence from observed runtime behavior and name
   unobserved paths explicitly.

In the review output, state whether agent-system review is applicable and name
the exact nodes and edges reviewed. Keep system findings within the requested
surface instead of broadening the rewrite.

## Output

For review-only requests, report prioritized findings first, their likely effect
on agent behavior, and unresolved assumptions. A replacement prompt is optional
unless requested. For rewrite or optimization requests, provide the replacement
Markdown prompt alongside the findings and assumptions.
