---
name: suggest-lucide-icons
description: Pick real Lucide icons for a concept, UI placement, button, section header, or note frontmatter. Use when the user asks what Lucide icon to use, requests icon candidates, or needs an icon name verified. Do not use for non-Lucide icon libraries or general icon or artwork design.
---

# Suggest Lucide Icons

Use this skill to choose existing Lucide icon names, not to invent symbolic
artwork. Optimize for recognizable meaning in the user's context.

## Workflow

1. When the project uses Lucide, inspect its manifest, lockfile-resolved version,
   and installed package first. Prefer installed assets or exact-version package
   assets as proof; `@latest` is not proof of project compatibility.
2. Identify the concept, action, object, state, and UI placement.
3. Generate 4-6 plausible Lucide icon names in kebab-case.
4. Verify candidates against installed, lockfile-resolved, or exact-version
   package assets. If no project version exists, confirm the icon through the
   official current package metadata or release, the current upstream package,
   or `https://lucide.dev/icons/<icon-name>`. Use
   [`context7-docs`](../context7-docs/SKILL.md) for current framework integration
   documentation when needed, not as sole proof of icon existence or version.
5. Discard names that cannot be verified.
6. Present up to 3 confirmed candidates and recommend one, stating the verification
   source and version.

If verification is blocked by network or tooling, say that candidates are
unverified and do not present them as confirmed.

## Naming Rules

- Use kebab-case: `arrow-up`, not `Arrow Up`.
- Use Lucide's American English names: `color`, not `colour`.
- For grouped variants, use the icon family first: `badge-plus`.
- For multiple elements, lead with the larger or containing element:
  `circle-user`, `square-arrow-out-up-right`.
- For modifiers, put the base object first: `circle-dashed`, not
  `dashed-circle`.

## Selection Rules

- Prefer icons whose visual metaphor works without explanation.
- Match the placement: toolbar actions need simpler shapes than navigation or
  section icons.
- Prefer action icons for commands (`save`, `download`, `trash-2`) and object or
  state icons for labels (`database`, `shield-check`, `file-warning`).
- Avoid novelty when a conventional icon exists.
- For multiple requested icons, choose a visually coherent set with similar
  density and stroke complexity.

## Output

```text
Candidates
- icon-name: why it fits
- icon-name: why it fits
- icon-name: why it fits

Recommendation: icon-name
Reason: ...
Verification: ...
```
