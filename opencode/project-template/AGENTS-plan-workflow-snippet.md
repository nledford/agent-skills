## Durable implementation-plan workflow

Use canonical plans at
`docs/implementation-plans/plans/<series>/<NN>-<slug>.md`. The series matches
`[a-z][a-z0-9-]{1,19}`; allocate the next zero-padded number as max+1 without
reusing gaps. `depends_on` is the authoritative execution prerequisite.

The Engineering Lead owns classification, integration, validation, and handoffs.
It may complete narrow work directly or delegate bounded, non-overlapping
implementation units only to `implementation-worker`. The worker cannot edit
durable plans, delegate, commit, push, deploy, or broaden its assigned scope.

The top-level Plan Orchestrator is the only durable plan and trusted-state writer.
The Engineering Review Board is a separate read-only primary agent, never a Task
child; invoke it directly for advisory review. Its critics and researchers do
not implement changes or approve plans.

Before first planned use, bootstrap must not overwrite the target repository's
`.gitignore`. After provisional state acquisition, add these missing exact lines
only when the existing policy is safe and non-conflicting:

```text
/.start-work/resume.json
/.start-work/lock/
```

Stop on broad, duplicate, ambiguous, or conflicting `.start-work` rules. Do not
copy the trusted helper into the target repository; it runs only from the linked
OpenCode checkout.

Material revisions increment `revision`, reset review and approval fields, and
require another review. Explicit human approval requires a matching ERB `ready`
record for the exact plan path, ID, revision, and baseline; persist every ERB
record through `/record-plan-review` before revision or approval. Approval
metadata updates do not increment revision. Execute only lifecycle-valid approved
plans with completed dependencies, matching approval, and unchanged or
re-reviewed baseline. Keep live OpenCode configuration machine-local.
