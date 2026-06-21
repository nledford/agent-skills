---
name: brainstorming
description: >
  Structured ideation for ambiguous software engineering work. Use when agents
  need to generate multiple options, compare tradeoffs, or converge on a
  recommendation before implementation, architecture, domain modeling, API
  design, migration, refactor, testing strategy, or unclear debugging work.
  Do not use for simple mechanical tasks, obvious single-path fixes, or work
  that first requires direct code inspection, tests, or a narrow change.
---

# Brainstorming

Use this skill to make option generation explicit before choosing a path. The
goal is better engineering judgment, not more ceremony.

## When to use

Load this skill when the task has meaningful uncertainty or more than one
plausible path:

- ambiguous product or engineering requirements;
- architecture, domain modeling, API design, migration, refactor, or testing
  strategy decisions;
- debugging situations where the cause is unclear and multiple hypotheses need
  comparison;
- planning that benefits from divergent thinking before convergence;
- decisions where maintainability, domain alignment, testability, simplicity,
  performance, security, operability, or migration cost may point in different
  directions.

## When not to use

Skip brainstorming when it would add ceremony without changing the outcome:

- simple, mechanical, formatting-only, generated, or already-specified tasks;
- tasks with an obvious single correct implementation;
- small fixes where reading the code and making the narrow change is enough;
- situations where the next honest step is direct repository inspection,
  reproduction, tests, or validation rather than ideation.

For active failures, load `systematic-debugging` first. Use brainstorming only
after the symptom is clear enough to compare hypotheses or solution paths.

## Workflow

1. **Frame the problem.** Restate the goal, constraints, known facts, and desired
   outcome in repository or domain language.
2. **Separate evidence.** List facts, assumptions, unknowns, and risks. Do not
   invent requirements or facts that are not grounded in the prompt, issue,
   repository docs, code, tests, or observed behavior.
3. **Generate options.** Produce at least two credible candidate approaches
   before selecting one. Include a conservative option when appropriate.
4. **Compare tradeoffs.** Evaluate maintainability, domain alignment,
   testability, simplicity, performance, security, operability, migration cost,
   reversibility, and fit with existing boundaries or coverage.
5. **Converge.** Recommend one path, explain why it is better than the credible
   alternatives, and name any rejected option that remains tempting.
6. **Plan validation.** Identify evidence that would validate or invalidate the
   recommendation: code to inspect, tests to add or run, docs to check, metrics,
   failure reproduction, or review gates.
7. **Transition.** Turn the recommendation into an actionable next step, a small
   implementation sequence, or a handoff to the appropriate implementation,
   methodology, debugging, or review skill.

## Output shape

Keep results concise enough for downstream implementation. Use this structure by
default and omit non-useful subsections:

```text
Problem framing
- Goal:
- Known facts:
- Constraints:

Assumptions, unknowns, and risks
- Assumptions:
- Unknowns:
- Risks:

Candidate options
1. Option A — ...
2. Option B — ...
3. Option C — ...

Tradeoff analysis
- Maintainability:
- Domain alignment:
- Testability:
- Simplicity:
- Performance/security/operability/migration cost:

Recommended approach
- Choose:
- Why:
- Rejected alternatives:

Validation plan
- Evidence to gather:
- Checks/tests/reviews:

Open questions
- Blocking only:
```

## Practice integration

- **BDD:** Use brainstorming to clarify behavior options and acceptance examples,
  not to replace executable scenarios or tests. If the outcome needs durable
  behavior contracts, load `behavior-driven-development` or `gherkin` next.
- **DDD:** Prefer existing domain language, boundaries, invariants, and policies
  when comparing options. Load `domain-driven-design` when the model itself needs
  focused design.
- **TDD:** Use the validation plan to decide the first failing test or regression
  check. Load `test-driven-development` when implementation should proceed by
  Red-Green-Refactor.

## Behavior examples

```gherkin
Scenario: Ambiguous API design benefits from brainstorming
  Given an agent sees two viable route or data-shape designs
  When the tradeoffs affect domain boundaries, tests, or migration cost
  Then the agent compares options before recommending an implementation path
```

```gherkin
Scenario: A narrow mechanical fix skips brainstorming
  Given the user asks for a clearly specified typo, formatting, or one-line bug fix
  When code inspection shows the implementation path is obvious
  Then the agent makes and verifies the narrow change without brainstorming ceremony
```

## Anti-patterns

- Generating only one option and calling it brainstorming.
- Treating brainstorming as a substitute for reading code, docs, tests, or error
  output.
- Producing vague ideas with no implementation implications.
- Overweighting quick wins when long-term maintainability, security, or domain
  alignment matters.
- Ignoring existing boundaries, invariants, test coverage, or validation lanes.
- Using brainstorming to avoid making a justified recommendation.
