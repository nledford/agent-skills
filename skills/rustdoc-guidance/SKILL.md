---
name: rustdoc-guidance
description: >
  Practical Rustdoc guidance for Rust API documentation and documentation tests.
  Use this skill whenever adding, changing, or reviewing Rust public APIs,
  crate/module docs, doctests, examples, unsafe contracts, panic/error docs,
  invariants, feature-flag notes, or maintainability docs for non-obvious Rust
  APIs. Also use when a task mentions rustdoc, `///`, `//!`, `cargo doc`,
  `cargo test --doc`, doctests, API examples, or missing-docs lints.
---

# Rustdoc Guidance

Use Rustdoc to make Rust APIs understandable at the call site and trustworthy in
generated documentation. Prefer clear names and simple design first; document the
contract that remains non-obvious.

## What rustdoc is

- `rustdoc` is Rust's documentation system. It ships with Rust and generates
  HTML API documentation from crate roots or Markdown files.
- Cargo drives it with `cargo doc` / `cargo doc --open`; examples in doc comments
  can be compiled and run with `cargo test --doc`.
- Rustdoc renders documentation comments and `#[doc = ...]` attributes into API
  docs. It documents public items by default.
- Comment forms:
  - `///`: outer documentation for the item that follows.
  - `//!`: inner documentation for the enclosing crate or module.
  - `//`: ordinary implementation comment; not rendered as API docs.

## Selection rules for agents

Load this skill when work touches Rust documentation as part of:

- implementing or refactoring public Rust APIs;
- adding crate-level or module-level docs;
- writing examples or documentation tests;
- reviewing Rust APIs for caller obligations, invariants, or maintainability;
- documenting unsafe code, panics, errors, side effects, lifetimes, ownership,
  performance, concurrency, feature flags, or platform behavior.

Related skills:

- Use `rust-best-practices` for broader Rust implementation choices.
- Use `rust-testing` for broader test strategy; remember nextest does not run
  doctests.
- Use `code-review` or `rust-testing-code-review` for requested reviews, but
  apply this skill's checklist to documentation findings.
- Use `AGENTS.md` and `docs/agents/` conventions for durable prose docs outside
  API comments.

## When rustdoc is mandatory

Add or update Rustdoc for:

- exported public APIs intended for external or cross-module use: crates,
  modules, structs, enums, variants, traits, functions, methods, constants,
  macros, and type aliases;
- APIs where callers must understand safety, ownership, lifetimes, panic
  behavior, errors, side effects, performance, threading, or invariants;
- every `unsafe` item and every API with caller obligations;
- names whose behavior is not obvious from the signature alone;
- domain concepts, boundaries, or workflows that future maintainers could misuse;
- APIs introduced or materially changed by a feature, plan, refactor, or domain
  boundary change where docs are needed for maintainability.

Also document important internal APIs when their behavior, invariants, or domain
semantics are non-obvious. Public visibility is not the only signal; misuse risk
is the signal.

## When not to use rustdoc

- Do not write `/// Gets the user id.` on `fn user_id(&self) -> UserId` unless
  there is a non-obvious contract.
- Do not use Rustdoc to compensate for bad names or overly complex design.
- Do not freeze stale implementation details that callers should not rely on.
- Use `//` for local implementation notes, algorithms, workarounds, and "why this
  line exists" comments that are not part of the API contract.
- Use durable docs (`docs/`, README, guides) for broad tutorials, architecture,
  operator procedures, or prose too large for API reference pages.

## What good rustdoc includes

Start with a short summary sentence; rustdoc uses the first paragraph in search
and module summaries. Add only sections that matter for callers.

Common sections:

- purpose and behavior;
- parameters and return values when the signature is not self-explanatory;
- `# Examples` for expected use;
- `# Errors` for `Result`-returning APIs;
- `# Panics` for reachable panic conditions;
- `# Safety` for `unsafe` items or unsafe caller obligations;
- invariants and domain rules;
- cancellation, threading, synchronization, or runtime behavior;
- performance, allocation, ordering, or complexity guarantees;
- feature flags, platform-specific behavior, and configuration requirements.

Prefer intra-doc links such as ``[`Iterator`]``,
``[`crate::module::Type`]``, or ``[`Self::method`]`` when they help navigation.
Keep links compiling if the crate uses `broken_intra_doc_links` lints.

## Doctest guidance

Include doctests when examples demonstrate public API usage or protect behavior
that readers will copy.

Good doctest candidates:

- non-trivial constructors, builders, or fluent APIs;
- edge cases and representative error handling;
- trait implementations and extension traits;
- domain workflows where the sequence matters;
- APIs with examples that should stay accurate after refactors.

Avoid doctests when examples require heavy external state, nondeterminism,
network services, databases, secrets, ambient `.env`, timing assumptions, or large
setup. Move those checks to unit, integration, or browser tests and keep the docs
example small.

Code block attributes:

- default `` ``` ``: compile and run; prefer this for most examples;
- `` ```no_run ```: compile but do not run; use for setup, I/O, or examples that
  would have side effects locally;
- `` ```ignore ```: neither compile nor run by default; use only as a last resort
  when the example cannot be made reliable;
- `` ```compile_fail ```: prove an invalid use does not compile;
- `` ```should_panic ```: show a panic contract when the panic itself is the point.

Use hidden setup lines starting with `#` to keep examples readable while still
compiling. Examples using `?` need a `main` returning `Result` or a hidden
`Ok::<(), E>(())` tail.

Doctests are tests. Maintain them like normal tests, and run the repo's Rustdoc
lane after changing executable examples.

## Maintainable examples

- Keep examples small, realistic, deterministic, and focused on one concept.
- Show expected caller usage, not private implementation mechanics.
- Prefer domain-relevant names and values for domain APIs.
- Avoid large copied setup; hide boring imports/setup with `#` lines or use helper
  APIs that are already part of the public surface.
- Avoid `unwrap()` in examples unless the example is explicitly about panic or the
  surrounding prose explains why failure is impossible; prefer `?` or assertions
  on `Result`.
- After refactors, update examples in the same change as the API so generated docs
  do not teach obsolete usage.

## Good and bad examples

Bad: restates the name and omits the caller contract.

```rust
/// Parses a manifest.
pub fn parse_manifest(input: &str) -> Result<Manifest, ManifestError> {
    /* ... */
}
```

Good: explains behavior, errors, and usage.

````rust
/// Parses a plugin manifest from TOML text.
///
/// The returned manifest is normalized so relative paths are resolved against the
/// manifest file's parent directory by the caller before registration.
///
/// # Errors
///
/// Returns [`ManifestError::Syntax`] when `input` is not valid TOML and
/// [`ManifestError::MissingField`] when a required manifest field is absent.
///
/// # Examples
///
/// ```
/// # use chidori_plugins::{parse_manifest, ManifestError};
/// let manifest = parse_manifest(r#"name = "resize""#)?;
/// assert_eq!(manifest.name(), "resize");
/// # Ok::<(), ManifestError>(())
/// ```
pub fn parse_manifest(input: &str) -> Result<Manifest, ManifestError> {
    /* ... */
}
````

Bad: documents a local implementation note as API reference.

```rust
/// Uses a HashMap because lookup was slow in the old vector implementation.
pub struct WorkspaceIndex { /* ... */ }
```

Better: document the stable behavior callers can rely on; keep the implementation
reason as `//` near the implementation if it still matters.

```rust
/// Indexes workspace entries by stable workspace id.
///
/// Lookups are independent of insertion order. Iteration order is unspecified.
pub struct WorkspaceIndex { /* ... */ }
```

Unsafe APIs must state caller obligations.

```rust
/// Returns a buffer view without checking UTF-8 validity.
///
/// # Safety
///
/// `bytes` must contain valid UTF-8 for the returned lifetime. The caller must
/// not mutate the underlying storage while the returned `&str` is live.
pub unsafe fn bytes_as_str_unchecked(bytes: &[u8]) -> &str {
    /* ... */
}
```

## Review checklist

When adding or reviewing Rustdoc, ask:

1. Does this item need Rustdoc because it is public, cross-module, unsafe,
   non-obvious, domain-heavy, or easy to misuse?
2. Is the first sentence a useful summary rather than a restatement of the name?
3. Does the prose describe caller-visible behavior instead of brittle internals?
4. Are errors, panics, safety requirements, side effects, ownership/lifetime
   expectations, concurrency, performance, feature flags, and invariants covered
   where relevant?
5. Are examples small, realistic, deterministic, and aligned with current API
   names?
6. Should an example be an executable doctest? If not, is `no_run`, `ignore`, or a
   normal test the better fit, and why?
7. Do doctests avoid secrets, services, databases, and excessive setup?
8. Are hidden setup lines used only to improve readability, not to hide important
   behavior?
9. Are intra-doc links accurate and helpful?
10. Did the relevant validation run (`cargo doc`, `cargo test --doc`, or the
    repository's Rustdoc lane)?

## Verification

- Prefer repository recipes over direct Cargo commands. In Chidori, run
  `just test-rustdoc` after adding or changing doctests.
- Use `cargo doc --no-deps -p <crate>` or the repository's doc-build lane when
  checking rendered docs or missing-docs behavior for one crate.
- Remember `cargo nextest` does not run doctests; pair nextest lanes with the
  Rustdoc lane when doc examples matter.

## Official references

- <https://doc.rust-lang.org/rustdoc/what-is-rustdoc.html>
- <https://doc.rust-lang.org/rustdoc/how-to-write-documentation.html>
- <https://doc.rust-lang.org/rustdoc/write-documentation/documentation-tests.html>
- <https://doc.rust-lang.org/rustdoc/write-documentation/the-doc-attribute.html>
- <https://doc.rust-lang.org/rustdoc/write-documentation/what-to-include.html>
