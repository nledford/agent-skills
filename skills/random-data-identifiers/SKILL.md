---
name: random-data-identifiers
description: Randomness, generated identifiers, and test data guidance. Use when generating random numbers, UUIDs, CUIDs, ULIDs, nonces, tokens, filenames, fixture data, seeded simulations, or collision-resistant IDs in code or tests. Prefer cryptographically secure randomness for secrets and IDs; use explicit seeded PRNGs for reproducible tests and simulations.
---

# Random Data and Identifiers

Use this skill whenever randomness or generated identifiers affect correctness,
security, reproducibility, storage, or test stability.

## Use When

- Generating random numbers, names, fixtures, fuzz/property inputs, seeds,
  temporary filenames, slugs, UUIDs, CUIDs, ULIDs, NanoIDs, nonces, tokens,
  passwords, invitation codes, reset links, API keys, cache keys, correlation IDs,
  primary keys, or public IDs.
- Reviewing collision risk, deterministic tests, reproducible simulations,
  snapshots, fixture factories, random ordering, shuffling, sampling, or flaky
  randomness-dependent behavior.
- Choosing between database-generated IDs, application-generated IDs, sequential
  IDs, sortable IDs, random IDs, or opaque public identifiers.

Do not use this skill for fixed example values with no randomness, or for ID
schema design that is purely database-native; use the SQL/PostgreSQL/SQLite skill
as well when constraints, indexes, or migrations are involved.

## Core Rules

1. Use cryptographically secure randomness by default for secrets, tokens,
   nonces, invitation/reset codes, password material, API keys, public IDs,
   unguessable filenames, auth/session data, and security-sensitive test data.
2. Use explicit seeded PRNGs for deterministic tests, simulations, fixtures,
   snapshots, generated examples, and reproducible bug reports. Record or print
   the seed only when it is not a secret.
3. Never use weak or convenience randomness for secrets or public unguessable IDs:
   no `Math.random()`, Python `random`, timestamps, counters, process IDs, or
   ad-hoc hashes for security-sensitive values.
4. Make collision handling explicit. A random ID still needs a uniqueness
   constraint, retry policy, or deterministic derivation strategy when collisions
   matter.
5. Keep test data readable unless randomness is the behavior under test. Most
   tests are clearer with fixed examples plus one seeded/generated edge case.

## Identifier Choice

- Use database sequences or auto-increment IDs for private relational identity
  when ordering and compact indexes matter and enumeration is not exposed.
- Use UUIDv4 or another secure random opaque ID for public, unguessable,
  distributed identifiers when sort order is not required.
- Use sortable IDs such as ULID/UUIDv7 only when time ordering materially helps
  storage, pagination, or operations. Treat embedded timestamps as information
  disclosure if IDs are public.
- Use CUID/NanoID-style IDs when the project already standardizes on them or
  needs short, URL-safe, collision-resistant identifiers. Inspect library quality,
  randomness source, alphabet, length, and maintenance before adding a package.
- Use slugs only for human-readable names. Pair slugs with immutable IDs when
  rename history, uniqueness, privacy, or enumeration matters.

## Language Guidance

- **Python:** use `secrets` for tokens and unguessable strings, `uuid.uuid4()` for
  random UUIDs, and `random.Random(seed)` for deterministic tests. Do not use the
  `random` module for secrets. Keep Faker/Hypothesis seeds explicit when used.
- **JavaScript/TypeScript:** use Web Crypto or Node.js crypto APIs such as
  `crypto.randomUUID()`, `crypto.getRandomValues`, or `randomBytes` for secure
  values. Use Bun crypto APIs only when the repository explicitly runs on Bun.
  Use deterministic PRNG libraries only when already present or clearly
  justified. Do not use `Math.random()` for IDs, tokens, or security-sensitive
  fixtures.
- **Rust:** inspect crate versions and features. Use OS-backed randomness or
  vetted crates for secrets and IDs, deterministic seeded RNGs for tests, and the
  `uuid`, `rand`, or project-standard ID crates only through reviewed APIs. Avoid
  leaking predictable seeds into production paths.
- **SQL:** enforce uniqueness with constraints or indexes. Prefer database-native
  generators only when the target engine, extension, replication model, and
  migration story are explicit.

## Test Data and Reproducibility

- Prefer named fixed fixtures for ordinary unit tests.
- Use generated data when it explores meaningful ranges, invariants, encodings,
  Unicode, ordering, time zones, nullability, or malformed inputs.
- For property tests and fuzzing, save the failing seed/input and convert durable
  regressions into focused examples when possible.
- Keep generated examples stable in docs and snapshots; uncontrolled randomness
  makes reviews noisy and examples misleading.
- Avoid random sleeps, ports, filenames, or clocks as a flake workaround. Use
  deterministic coordination, temporary directories, and explicit cleanup.

## Review Checklist

- Is the random value security-sensitive, public, persistent, sortable, or only a
  local test helper?
- Is the randomness source appropriate for that classification?
- Is the alphabet, length, entropy, and encoding sufficient for collision and
  guessing risk?
- Are uniqueness constraints, retries, and error handling present where needed?
- Are tests deterministic or explicitly seed-reporting?
- Are generated IDs documented as stable or unstable API fields where clients may
  depend on them?

## Anti-Patterns

- Timestamp-plus-random suffixes for secrets or public IDs.
- Hashing predictable input and calling it random.
- Using deterministic seeds in production because tests needed reproducibility.
- Committing snapshots, docs, or fixtures that churn on every run.
- Depending on ID lexical order without choosing a sortable ID format and index
  strategy deliberately.
