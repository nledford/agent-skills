---
name: gherkin
description: Write clear, idiomatic Gherkin feature specifications. Use when creating or editing .feature files, BDD scenarios, Given/When/Then examples, Scenario Outlines, Examples tables, Background sections, or business-readable acceptance criteria.
---

# Gherkin

Use Gherkin to write business-readable behavior specifications that can be
reviewed by non-engineers and connected to automated tests. Use the official
Gherkin reference as the conceptual baseline:
https://cucumber.io/docs/gherkin/reference

## Core Structure

```gherkin
Feature: Short description of the capability

  Rule: Optional business rule that groups related scenarios

    Background:
      Given shared context for every scenario in this rule

    Scenario: Specific behavior title
      Given relevant context
      When the actor performs the meaningful action
      Then an observable outcome occurs
```

Use only the structure needed for clarity. A small feature may need only
`Feature` and a few `Scenario` blocks.

## Keyword Guidance

- `Feature`: name the capability or business goal, not a component.
- `Rule`: group scenarios that demonstrate one business rule.
- `Scenario`: use for one concrete example.
- `Scenario Outline`: use when the same behavior must be exercised with several
  meaningful data variations.
- `Examples`: keep tables small and focused on the variables that change the
  outcome.
- `Background`: use only for shared context that every scenario in the feature or
  rule genuinely needs.
- `Given`: establish relevant preconditions or state.
- `When`: describe the single meaningful action or event.
- `Then`: describe observable outcomes.
- `And` / `But`: continue the previous step type when it improves readability;
  do not use them to hide multiple unrelated behaviors.

## Writing Good Steps

Good steps are declarative:

```gherkin
Given Avery has an active workspace membership
When Avery uploads a duplicate photo
Then the upload is rejected as a duplicate
And the original photo remains unchanged
```

Avoid UI scripts and implementation details:

```gherkin
Given the user is on "/photos/new"
When they click "Choose File" and click "Upload"
Then the API returns 409
And the duplicate_photos table has 1 row
```

Use UI, HTTP, or database details only when they are the behavior contract being
specified.

## Scenario vs Scenario Outline

Use `Scenario` when one concrete example communicates the behavior clearly.

Use `Scenario Outline` when:

- The same rule has several important input/output pairs.
- The examples table is shorter and clearer than repeated scenarios.
- Each row protects a distinct case that should fail independently.

Do not use `Scenario Outline` just to compress unrelated behaviors into one
table. Split scenarios when the narrative, preconditions, or expected outcomes
change meaningfully.

## Background Discipline

Use `Background` sparingly:

- Keep it short, usually one to four steps.
- Include only context that every scenario needs.
- Avoid important assertions in `Background`; scenarios should contain their own
  outcomes.
- Prefer explicit scenario setup when shared setup makes the scenario hard to
  understand.

## Readability Rules

- Write concise scenario titles that finish the sentence "Scenario: ...".
- Keep feature files readable by product, QA, support, and domain experts.
- Prefer domain terms over technical terms.
- Avoid duplicate scenarios that assert the same rule with unimportant data
  changes.
- Keep steps stable across UI redesigns and implementation refactors.
- Align step wording with existing step definitions when editing an established
  suite, but do not preserve misleading wording if it obscures behavior.

## Validation Checklist

- The file uses valid Gherkin keywords and indentation.
- Every scenario has at least one observable `Then`.
- Each `When` describes the behavior-triggering action or event.
- Examples tables have headers and values for every parameter.
- No scenario depends on order from another scenario.
- Tags, if used, describe execution needs or meaningful categories rather than
  temporary implementation notes.

## Language Usage

- **Python:** map feature steps to pytest-bdd, behave, or project-specific
  adapters only when the repository already uses them or the user explicitly asks
  for executable `.feature` files. Keep step definitions thin and push domain
  rules into Python modules with ordinary tests.
- **Rust:** use Cucumber-style crates or custom feature runners only when the
  repository already has that lane. Otherwise keep Gherkin as acceptance criteria
  and implement behavior with Rust unit/integration tests.
- **JavaScript/TypeScript and other languages:** connect `.feature` files to the
  existing test runner only when it improves stakeholder-readable coverage. Do
  not introduce a Gherkin runner for simple changes where clear test names or
  inline Given/When/Then notes would be enough.
