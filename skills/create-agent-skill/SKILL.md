---
name: create-agent-skill
description: Create or improve reusable agent skills. Use when the user asks to create a new skill, update an existing skill, define skill instructions, scaffold a SKILL.md-based skill directory, validate skill structure, or turn repeated agent workflows into a global or project skill. Do not use for ordinary documentation edits, application implementation, or ignored third-party runtime skills.
---

# Create Agent Skill

This skill helps create concise, maintainable agent skills that future agents can reliably use. Treat a skill as reusable operating instructions for a recurring task, not as a transcript of one solution.

## Workflow

1. Clarify the goal only as much as needed.
   - Identify the task the skill should help agents perform.
   - Ask for missing requirements only when a reasonable default would be risky.
   - Infer defaults when the user has already provided the purpose, scope, target location, or examples.
   - State assumptions briefly before implementing them.

2. Inspect local conventions before writing.
   - Look for existing skills in the requested skill root, commonly `~/.agents/skills` for global agent skills.
   - Follow the target repository's ownership policy before editing a repository
     skill. When it provides them, classify an ambiguous target directory with
     `just list-first-party`, `just list-third-party`, or `just inspect <skill>`.
     Treat lockfile-owned or ignored runtime installs as third-party only when
     repository policy or inspection commands establish that classification;
     otherwise leave ownership unresolved until evidence distinguishes source
     from runtime installs.
   - Match the local file names, frontmatter style, optional metadata, resource folders, and validation tools already in use.
   - In this repository, consult [`docs/skill-taxonomy.md`](../../docs/skill-taxonomy.md) before adding, deleting, splitting, merging, or renaming first-party skills.
     Use [`docs/cross-reference-map.md`](../../docs/cross-reference-map.md) for related-skill routing, and apply the taxonomy rubric and
     [`docs/skill-review-checklist.md`](../../docs/skill-review-checklist.md) before handoff.
   - Do not invent a different skill format when a local convention exists.
   - Load [`documentation-engineering`](../documentation-engineering/SKILL.md) for skill-document quality. For a requested or final review, also load
      [`code-review`](../code-review/SKILL.md) and [`review-verification-protocol`](../review-verification-protocol/SKILL.md).

3. Define the skill contract.
   - Name the users, tasks, inputs, outputs, and success criteria.
   - List activation triggers: user phrases, file types, domains, tools, or workflows that should load the skill.
   - List non-goals so the skill does not silently expand into unrelated work.
   - Decide whether optional `scripts/`, `references/`, or `assets/` resources are genuinely useful. Do not add empty or placeholder resource folders.

4. Choose the directory name.
   - Use lowercase letters, digits, and hyphens only.
   - Prefer short, verb-led names such as `create-agent-skill`, `fix-ci-checks`, or `summarize-incident`.
   - Keep the folder name and frontmatter `name` identical.
   - Avoid vague names such as `helper`, `workflow`, or `assistant`.

5. Write the skill.
   - Put required trigger information in the frontmatter `description`; the body loads only after the skill is selected.
   - Keep the body procedural and reusable. Prefer checklists, decision rules, and compact examples over long explanations.
   - Use imperative instructions that tell the agent what to do.
   - Include constraints, assumptions, and non-goals when they affect behavior.
   - Include examples only when they clarify activation, output quality, or common mistakes.
   - Avoid project-local paths, private repository assumptions, secrets, personal names, or one-off details unless the user explicitly wants a private local skill.

6. Validate and refine.
   - Confirm the required files exist and the directory lives in the requested skill root.
   - Confirm frontmatter parses as YAML and includes at least `name` and `description`.
   - Confirm the `description` explains both what the skill does and when it should activate.
   - Confirm first-party resource files are linked from `SKILL.md`, local Markdown links resolve, and there are no draft placeholders, stale examples, or unnecessary files.
   - Run any local validator or skill CLI if available. If not, perform a manual structure and content review.
   - Test the skill mentally against at least two realistic user requests: one that should trigger it and one that should not.

## Minimal Structure

Follow the local convention if it differs, but a simple SKILL.md-based skill usually looks like this:

```text
skill-name/
`-- SKILL.md
```

Use this frontmatter pattern unless the local format requires additional fields:

```markdown
---
name: skill-name
description: What the skill helps with. Use when the user asks for specific trigger scenarios, task types, file types, or workflows.
---
```

Add optional resources only when they carry reusable value:

```text
skill-name/
|-- SKILL.md
|-- scripts/      # deterministic commands or helpers the agent can run
|-- references/   # detailed docs loaded only when needed
`-- assets/       # templates or files used in generated output
```

## Instruction Quality Rules

- Make instructions specific enough to guide behavior, but not so narrow that they only solve one prompt.
- Prefer "inspect existing files before editing" over "always use file X" unless the file is guaranteed by the skill.
- Prefer "ask if the target system is unknown" over asking for every detail up front.
- Use examples to distinguish good and bad behavior, not to restate the workflow.
- Avoid ambiguous verbs like "handle", "support", or "optimize" unless followed by concrete actions.
- Remove setup history, author notes, release notes, and general README content from the skill.

## Good and Bad Patterns

Good description:

```yaml
description: Create or update GitHub pull request review responses. Use when the user asks to address review comments, inspect unresolved PR threads, implement requested changes, or summarize reviewer feedback.
```

Bad description:

```yaml
description: Helps with GitHub.
```

Good workflow instruction:

```markdown
1. Fetch the PR metadata and unresolved review threads.
2. Separate actionable code-change requests from discussion-only comments.
3. Implement the smallest change that satisfies each actionable thread.
4. Run the relevant tests and summarize unresolved risks.
```

Bad workflow instruction:

```markdown
Do a great job and make the PR better.
```

Good scope control:

```markdown
Do not rewrite unrelated modules while addressing review comments unless the review specifically requires it.
```

Bad scope control:

```markdown
Improve anything that looks wrong.
```

## Maintenance Checklist

Before finishing a new or updated skill, verify:

- The skill name, folder name, and frontmatter `name` match.
- The frontmatter `description` contains activation guidance.
- The body is concise, procedural, and free of one-off context.
- Project names, modules, paths, recipes, frameworks, and validation commands
  come from target-repository evidence; examples use portable placeholders and
  do not encode source-project or machine-local assumptions.
- Optional resources are referenced from `SKILL.md` and are actually needed.
- Examples are realistic and transferable.
- Constraints and non-goals are explicit where they prevent misuse.
- The skill can be understood by a future agent without reading this creation conversation.
- Repository taxonomy or inventory docs are updated when the skill set changes.
- The repository skill review checklist has been applied when working on
  first-party skills.
