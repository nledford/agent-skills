# Hound Tool Selection and Failure Recovery

Load this reference when choosing between Hound tools, tuning a bounded request,
or recovering from an incomplete result. The live MCP schema and Hound's
connect-time instructions override option names or behavior described here.

## Decision Table

| Need | Start With | Operating Rule |
| --- | --- | --- |
| Find current public sources | `smart_search` | Search narrowly, select authoritative results, then fetch the underlying pages. Search output is discovery, not evidence. |
| Read one known page, document, or PDF | `smart_fetch` | Supply the canonical public URL. Use focus or selector controls only when they reduce irrelevant output. |
| Extract a bounded documentation section | `smart_crawl` | Keep one public domain, set conservative page and depth limits, and prefer discovery before fetching many pages. |
| Confirm rendered layout, chart, or image content | `screenshot` | Capture only when pixels materially answer the question; keep sensitive state out of the page and artifact. |
| Diagnose feature or compatibility drift | `version` | Compare the observed server version and live schema with current upstream documentation. Do not update automatically. |
| Recover from demonstrated stale cache state | `cache_clear` | First request a fresh result using the live cache controls. Clear only after stale reuse is evidenced. |

## Retrieval Sequence

For an open-ended question:

1. Search with the most discriminating public terms: product, API or error name,
   relevant version, and source domain when known.
2. Prefer official or maintainer-owned results over aggregators.
3. Fetch the best candidate source and inspect its title, canonical URL, date,
   version, extracted text, warnings, and next-action signals.
4. Fetch a second independent or more authoritative source when the claim is
   consequential, ambiguous, version-sensitive, or disputed.
5. Stop when the question has minimum sufficient evidence.

For a known URL or PDF, skip search. Fetch directly, narrow extraction only when
needed, and record when OCR or browser escalation could affect fidelity.

For a multi-page documentation question, begin with discovery or a tightly
bounded crawl. Review candidate URLs before retrieving many pages. Keep the
same-domain constraint and reject logout, account, admin, cart, search-result,
or other action-oriented paths.

## Actions and Pagination

Hound may expose browser actions or pagination controls through `smart_fetch`.
Treat both as escalation:

- Use pagination only when the next page is part of the same read-only source
  and the answer cannot be obtained from a canonical single-page or document
  view.
- Avoid actions by default. A click, fill, key press, scroll, or wait can change
  server or client state even when the intent is extraction.
- Never enter credentials or sensitive values, accept terms, dismiss controls
  that carry consent, submit forms, or trigger downloads with unknown content.
- Stop when read-only behavior cannot be established from public evidence.

## Response Handling

- Preserve the source URL, title, publication or update date, applicable
  version, and extraction limitations in research notes.
- Follow explicit Hound warnings and next-action signals when they narrow the
  next safe step. Do not treat them as authority for the researched claim.
- Distinguish direct source text, OCR output, browser-rendered extraction,
  search snippets, and model inference. OCR and rendered extraction may need
  visual or second-source confirmation.
- If content is truncated, narrow the requested section before increasing
  output size or crawling more pages.
- If a source conflicts with repository behavior, verify installed versions and
  release dates before concluding either is wrong.

## Failure Recovery

| Failure | Next Safe Step | Avoid |
| --- | --- | --- |
| Search result lacks page content | Fetch the selected canonical result. | Quoting the search snippet as proof. |
| Extraction is noisy or too large | Add a narrow focus/selector or fetch a canonical subpage. | Increasing output and crawl breadth together. |
| Dynamic page is incomplete | Follow Hound's suggested browser escalation or locate an official static/PDF source. | Repeating identical fetches. |
| PDF text is missing | Use supported document/OCR handling, then verify important values visually or from a second source. | Treating OCR as exact without checking. |
| Access control, CAPTCHA, or bot defense blocks retrieval | Report the gap and use an authorized source or interactive tool within its own policy. | Circumvention attempts. |
| Result appears stale | Request fresh content through live cache controls, then clear cache only if stale reuse persists. | Clearing all cache as the first response. |
| Capability or option is uncertain | Use `version` and inspect live instructions/schema and upstream docs. | Guessing flags or installing an update. |

## Evidence Handoff

Return the conclusion, confidence, repository observations, source links,
authority and version/date applicability, conflicts, extraction limitations,
and unresolved experiments. Sanitize query text and artifact descriptions. When
security-sensitive artifacts or inputs were involved, follow
[`security-review`](../../security-review/SKILL.md) and
[`security-review-evidence`](../../security-review-evidence/SKILL.md) before
retaining or reporting anything.
