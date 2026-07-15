## Durable implementation-plan workflow

Use canonical plans at
`docs/implementation-plans/plans/<series>/<NN>-<slug>.md`. The series matches
`[a-z][a-z0-9-]{1,19}`; allocate the next zero-padded number as max+1 without
reusing gaps. The path supplies plan identity. New and updated plans use exactly
the closed lean shape in `docs/implementation-plans/TEMPLATE.md`: no frontmatter,
lifecycle fields, review records, history, or additional sections. Resolve a
central choice conversationally rather than adding an open-decision section.
Existing lifecycle-style plans are immutable legacy evidence; create a new
max-plus-one lean successor instead of modifying them.

The Engineering Lead owns classification, integration, validation, and handoffs.
It may complete work directly whenever scope, safety, and validation are
adequate, including complex work; complexity may justify recommending a plan but
never creates one automatically. It may delegate bounded, non-overlapping
implementation units only to `implementation-worker`. The worker cannot edit
durable plans, delegate, commit, push, deploy, or broaden its assigned scope.

The Engineering Lead and Engineering Review Board may request bounded read-only
`plan-consultant` advice. The consultant cannot inspect `.start-work/**`,
mutate, delegate, create or authorize a plan, invoke `/start-work`, or begin
implementation. The ERB is a separate, optional read-only primary agent, never a
Task child; its critics and researchers do not implement changes or control plan
or state work.

Only an explicit human `/create-plan` request creates and persists a plan, and it
is plan-only. Execution-only `/start-work` accepts an existing valid canonical
lean plan path or validated no-argument resume pointer with explicit human
confirmation; it rejects free-form creation and plan-update requests. Explicit
plan-only updates are top-level Plan Orchestrator requests, not `/create-plan`
updates or `/start-work`.
`/convert-tapestry-plan` is always plan-only; execution requires a separate
human `/start-work <destination>` choice. The Plan Orchestrator is the only
durable plan and trusted-state writer.

Before first planned use, bootstrap must not overwrite the target repository's
`.gitignore`. After provisional state acquisition, add these missing exact lines
only when the existing policy is safe and non-conflicting:

```text
/.start-work/resume.json
/.start-work/lock/
```

Stop on broad, duplicate, ambiguous, or conflicting `.start-work` rules. Do not
copy the trusted helper into the target repository; it runs only from the linked
OpenCode checkout. The Plan Orchestrator acquires trusted provisional ownership
before mutating plan or state, validates the contained non-symlinked plan path,
and records only observed plan and state evidence. While retaining that lock, it
may construct a commit only for an explicit current human request or bounded plan
TODO: derive exact repository-relative paths from fresh trusted worktree evidence,
use `git add --`, recheck the staged diff and resulting worktree, and retain lock
and staged state on failure or uncertainty. A validated active canonical plan may
be staged, but Bash remains forbidden from mutating or redirecting plan bytes.
Approval is an additional human check, not proof a path is safe: separately
enumerate each dirty repository-relative path, quote it as one literal shell
word, and stop on `*`, `?`, bracket expressions, braces, pathspec magic, `.`,
traversal, substitution, or any other expansion syntax that cannot be represented
literally under the command policy.
The worker cannot stage or commit; amend, hook/signing bypass, implicit staging,
fetch, push, and branch/ref/history/worktree/remote mutation remain forbidden.
Load `git-commit`, plus `security-review` and `security-review-evidence` when
Git trust boundaries apply. Keep live OpenCode configuration machine-local; quit
and fully restart OpenCode before definition changes grant authority, because the
running session remains unchanged.
