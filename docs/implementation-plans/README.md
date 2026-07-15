# Implementation Plans

This directory holds project-local execution contracts. A new plan is a lean,
metadata-free document, not a lifecycle, review, approval, or execution record.

## Canonical Location and Identity

Plans live at:

```text
docs/implementation-plans/plans/<series>/<NN>-<slug>.md
```

- `series` matches `[a-z][a-z0-9-]{1,19}`.
- `NN` ranges from `01` through `99` and is the series maximum plus one. Gaps and
  retired numbers are never reused; a series whose maximum is `99` is exhausted.
- The path supplies identity; do not repeat a plan ID, sequence, status, baseline,
  owner, date, revision, review, approval, provenance, or execution state in the
  plan body.

## Lean Plan Format

Every newly created, updated, succeeded, or converted plan has exactly the body
shape in [TEMPLATE.md](TEMPLATE.md), with no frontmatter or additional sections.
The Context labels retain only the original request, decision-relevant repository
findings, and prerequisites that an executor cannot safely ignore. TODOs are
ordered, bounded, numbered Markdown checkboxes. Resolve decisions through the
plan's authorized sections rather than adding an open-decision ledger, history,
amendment, alternatives, or execution record.

## Human-Controlled Lifecycle

Direct implementation may proceed when scope, safety, and validation are
adequate; complexity may justify recommending a plan but never creates one
automatically. The Engineering Lead or ERB may request read-only
`plan-consultant` advice. Explicit `/create-plan` creates and persists a plan
only, while execution-only `/start-work` accepts an existing valid canonical lean
plan or validated no-argument resume pointer with explicit human confirmation.
Explicit plan-only updates are top-level Plan Orchestrator requests, not
`/create-plan` updates or `/start-work`. `/convert-tapestry-plan` is always
plan-only; execution requires a separate `/start-work <destination>` choice.

## Legacy Plan Succession

Existing verbose plans with lifecycle metadata or history are immutable legacy
artifacts. Do not mutate, normalize, or execute them in place. Their filenames
remain part of the series allocation inventory. When work based on a legacy plan
needs a new plan, allocate a new maximum-plus-one successor in that series and
write only the lean format; sequence order alone does not create a dependency.

Tapestry conversion remains available. A conversion destination is a newly
allocated lean plan; its source stays unchanged.

## Safe Plan Writes

Path permissions are defense in depth, not a sandbox against hostile repository
content or runtime bugs. Before any durable write, reject symlinked plan roots or
destination components and verify that the resolved destination remains under
`docs/implementation-plans/`. Do not cross the boundary with an apply-patch move,
shell redirection, alternate path spelling, or symlink alias.
