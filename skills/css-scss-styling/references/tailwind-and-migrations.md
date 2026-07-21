# Tailwind And Stylesheet Migrations

Load this reference only when Tailwind selection, adoption, upgrade, source
detection, or a CSS-to-SCSS migration is materially in scope. Keep the core
workflow in `SKILL.md` for ordinary stylesheet work.

## Tailwind CSS Decision Rules

Tailwind CSS is a utility-first styling framework and build workflow. Authors
compose small presentational classes, including responsive and state variants,
in markup or components; Tailwind scans configured source files for recognizable
class tokens and emits the corresponding CSS. It is not a replacement for the
CSS language: its output is CSS, and custom CSS remains appropriate where
utilities are not the clearest or safest expression.

Choose the primary authoring approach from repository evidence and the change's
ownership boundary:

| Prefer | When and why |
| --- | --- |
| Tailwind | The repository already uses it and the change fits its tokens, variants, component conventions, and build pipeline; or an explicit adoption has a bounded UI scope, stable source scanning, compatible browser targets, and a team preference for composing styles in markup. It is especially useful for token-constrained product UI, repeated responsive/state variants, and component/template systems that own their class strings. |
| Plain CSS | The repository already uses CSS; the change is small or global; selectors must target editorial, generated, third-party, or otherwise uncontrolled markup; the style depends on complex cascade/selectors or highly dynamic values; or adding a scan/build framework would create a second styling system. CSS is also preferable for portable framework-neutral output and runtime custom-property theming. |
| SCSS | The repository already has Sass and the problem benefits materially from compile-time maps, mixins, functions, or generated rules; or adopting Tailwind would add more migration and build risk than it removes. Confirm exact Tailwind/Sass compatibility before combining toolchains. |
| Intentional hybrid | The repository already separates responsibilities clearly, such as Tailwind for component composition and plain CSS for base styles, rich content, third-party markup, or bespoke selectors. Keep a single owner for each token and component; a hybrid is not permission to duplicate every rule in both systems. |

Do not introduce Tailwind when:

- The request is an isolated style change in a project with a working CSS, SCSS,
  CSS-module, or CSS-in-JS system.
- The project cannot reliably scan all class-bearing source files, generated
  templates, shared packages, or runtime content.
- The supported browsers, build environment, deployment model, or content
  security constraints are incompatible with the installed major's documented
  requirements.
- Most styling targets markup the project does not control, or the design is
  deliberately bespoke and would depend heavily on arbitrary values and custom
  plugins.
- Adoption would require a broad rewrite, reset/cascade change, or new token
  system that the task did not authorize.

When Tailwind is appropriate:

1. Use the repository's package manager and framework integration for the exact
   installed major. Preserve the existing stylesheet entrypoint, plugin order,
   generated-output policy, and development/build commands.
2. Keep candidate class names complete and statically recognizable in source.
   Map props or variants to complete class strings instead of constructing
   fragments such as `bg-${color}-500`. Use a documented source-registration or
   safelist mechanism only for genuinely external or generated inputs, not to
   hide an unbounded dynamic-class design.
3. Use the version-appropriate theme/configuration surface for shared design
   tokens. Use ordinary CSS custom properties when a value should exist at
   runtime without creating a utility API. Promote repeated arbitrary values
   into named tokens or custom utilities.
4. Keep responsive, dark-mode, motion, pointer, focus-visible, disabled, and
   other state variants consistent with local conventions and accessibility
   requirements. Do not encode behavior-critical state only through color or
   motion.
5. Extract repeated markup into the repository's components, templates, or
   partials before inventing a parallel semantic class layer. Write custom CSS
   for complex selectors, uncontrolled rich content, or a clearer bounded
   abstraction. Use `@apply` only when local conventions and the installed
   version support it.
6. Review Tailwind's base-style/reset behavior, including Preflight when present,
   before adoption or upgrades. Check form controls, headings, lists, media,
   borders, third-party widgets, and application base styles for changed browser
   defaults.
7. Verify the production build, generated CSS, source detection for every
   package/template boundary, browser-visible states, accessibility behavior,
   and output size. Source-string assertions and formatter success do not prove
   that a required utility was generated or renders correctly.

## Safe Tailwind Adoption Or Migration

1. Require an explicit adoption or migration goal. Record why Tailwind is a
   better fit than extending the existing CSS/SCSS system, which UI boundary is
   in scope, and what remains out of scope.
2. Inventory stylesheet entrypoints, tokens, resets/base styles, cascade order,
   source roots, shared packages, generated templates, class-name consumers,
   browser targets, tests, and generated-asset/deployment policy.
3. Add or upgrade Tailwind through the repository's normal dependency workflow
   and the official instructions for the exact major and framework. Do not
   hand-edit lockfiles or assume configuration from another major.
4. Prove the pipeline on a bounded representative slice. Preserve one styling
   owner per component and token, and avoid a long-lived state where equivalent
   CSS and utilities compete for the same elements.
5. Review base-style and cascade effects separately from component conversion.
   Keep rollback possible by isolating entrypoint and configuration changes from
   later mechanical migrations.
6. Validate development and production builds, source detection across package
   boundaries, generated output and size, visual/browser states, accessibility,
   and deployment/cache behavior before expanding the migration.

## Safe CSS-To-SCSS Migration

1. Confirm a migration is justified. If modern CSS solves the need, keep CSS and
   document why no preprocessor was added.
2. Inventory entrypoints, imports, static references, test snapshots, generated
   assets, cache keys, and deployment paths.
3. Add Sass through the repository's package/build workflow; do not hand-edit
   lockfiles or generated bundles.
4. Rename incrementally (`.css` to `.scss`) and keep CSS-compatible syntax first.
   Update imports, HTML links, template references, and build scripts together.
5. Introduce SCSS features only after compilation matches the old output closely
   enough to review. Prefer `@use`/`@forward` modules over `@import`.
6. Validate compiled CSS, app build, visual or browser tests, accessibility states,
   and cache/deploy behavior. Compare output size and selector changes when risk
   is high.

Migration risks include broken asset URLs, changed cascade order, duplicated or
missing emitted CSS, CSS module class-name changes, source-map drift, framework
watcher failures, CI images missing Sass, and visual regressions hidden by broad
snapshots.
