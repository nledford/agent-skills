# Skill Review Checklist

Use this quick pass when creating, editing, or reviewing first-party skills. It
complements the [skill taxonomy](skill-taxonomy.md) and
[cross-reference map](cross-reference-map.md); do not duplicate their full
tables or skill bodies here.

## Checklist

- [ ] **Frontmatter:** `name` matches the directory and `description` is present.
- [ ] **Activation:** `description` names the task surface, trigger verbs, file
  types, tools, domains, and near-miss exclusions needed for routing.
- [ ] **Non-goals:** the body says when not to load the skill or when to route to
  an adjacent skill.
- [ ] **Links and resources:** optional `references/`, `scripts/`, `templates/`,
  or `assets/` files are useful, linked from `SKILL.md`, and reachable; no empty
  resource folders or placeholders remain.
- [ ] **Taxonomy inventory:** update the taxonomy inventory, coverage, and
  boundary notes when a skill is added, removed, renamed, split, merged, or
  materially re-scoped.
- [ ] **Change notes:** add a short change note only when skill churn creates
  reviewer confusion, repeated audit questions, or user-facing upgrade needs;
  do not create or maintain a changelog otherwise.
- [ ] **Related-skill routing:** cross-links and cross-reference-map entries only
  exist when they change activation, execution, or validation choices.
- [ ] **Runtime governance, when applicable:** guidance that mentions agents,
  Task delegation, commands, durable plans, implementation, or review treats
  skills as procedures rather than runtime IDs and matches the
  [engineering agent governance guide](engineering-agent-governance.md).
- [ ] **Examples:** examples and counterexamples are short, transferable,
  sanitized, and maintained by tests or easy manual validation where practical.
- [ ] **Security evidence:** trust-boundary, secret, dependency, command, file
  path, or credential-adjacent work routes to `security-review` and
  `security-review-evidence`; report only sanitized, verified evidence.
- [ ] **Validation:** run `just validate` for skill metadata, taxonomy,
  cross-reference, resource, and link changes; run `just check` for broader
  repository changes. The underlying validator is
  `python3 tools/skills_manager.py validate` when a direct script call is needed.
  Run narrower checks for changed scripts, examples, or generated resources when
  present.
- [ ] **Handoff:** report changed files, validation output, skipped checks,
  unresolved risks, and at least one should-trigger and should-not-trigger
  scenario considered.
