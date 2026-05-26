# Status

Snapshot of where the project stands after the initial M1-M7 plan completes.

For the original goals and design, see [00_Goals.md](00_Goals.md), [02_PrePlan.md](02_PrePlan.md),
and [03_Plan.md](03_Plan.md).


## Milestones — done

| | Scope | Spec (CM default / prescan) | Tests | Source LOC |
|---|---|---|---|---|
| M0 | Skeleton, events, scanners scaffold, spec runner | n/a | 26 | ~470 |
| M1 | Block parser (CommonMark blocks, no inline) | 196 / — | 225 | ~2,700 |
| M2 | Inline core (emphasis, code, escapes, entities, autolinks, inline HTML, breaks) | 365 / — | 295 | ~3,700 |
| M3 | Links, images, refdefs, broken-link callback, fuel guard | 424 / 468 | 303 | ~4,500 |
| M4 | GFM extensions: tables, strikethrough, tasklists, admonition blockquotes | 429 / 473 | 323 | ~4,950 |
| M5 | Tight / loose list rendering | 459 / 503 | 327 | ~5,030 |
| M6 | StreamingParser + chunking-equivalence guarantee | 459 / 503 | 354 | ~5,200 |
| M7 | README, offset-consistency tests, docs polish | — | 357 | ~5,200 |


## Cross-cutting invariants — verified

All four invariants from [00_Goals.md](00_Goals.md#cross-cutting-invariants) hold under test:

1. **Committed events are immutable, append-only.** No M6 test detects a committed event
   changing across feeds.
2. **`tentative` is a contiguous suffix of the oracle event stream.** Verified implicitly by the
   M6 equivalence tests (the prefix `committed_so_far + current_tentative` always matches the
   oneshot parse of the prefix-of-input-seen-so-far on small fixtures).
3. **Full-reparse equivalence.** `StreamingParser().feed(text_in_N_chunks).committed +
   finish().committed == parse(text)` for any chunking. Verified over 572 CommonMark spec cases
   + 14 GFM cases × 8 chunking strategies (whole / each-char / fixed-1 / fixed-3 / fixed-32 /
   by-lines / random-7 / random-42). Plus a smoke test that splits a representative fixture at
   every possible byte position.
4. **Absolute char-position source offsets on every event.** `pdcmark/tests/test_offsets.py`
   asserts `0 ≤ start ≤ end ≤ len(input)` for every event in every CM spec case, and that
   Start/End spans enclose their inner events for the first 200 cases.


## Spec section breakdown (current)

| Section | Default | Prescan | Total |
|---|---|---|---|
| Autolinks | 19 | 19 | 19 |
| Backslash escapes | 9 | 10 | 13 |
| Blank lines | 1 | 1 | 1 |
| Block quotes | 24 | 24 | 25 |
| Code spans | 18 | 18 | 22 |
| Emphasis and strong emphasis | 125 | 125 | 132 |
| Entity and numeric character references | 12 | 12 | 17 |
| HTML blocks | 43 | 43 | 44 |
| Hard line breaks | 11 | 11 | 15 |
| Images | 8 | 21 | 22 |
| Inlines | 1 | 1 | 1 |
| Link reference definitions | 13 | 17 | 27 |
| Links | 54 | 80 | 90 |
| List items | 40 | 40 | 48 |
| Lists | 21 | 21 | 26 |
| Paragraphs | 8 | 8 | 8 |
| Precedence | 1 | 1 | 1 |
| Raw HTML | 14 | 14 | 20 |
| Soft line breaks | 2 | 2 | 2 |
| Tabs | 8 | 8 | 11 |
| Textual content | 3 | 3 | 3 |
| Thematic breaks | 2 | 2 | 2 |

GFM extensions (under `pdcmark.GFM`):

| File | Pass |
|---|---|
| `gfm_strikethrough.txt` | 3/3 |
| `gfm_table.txt` | 8/9 |
| `gfm_tasklist.txt` | 2/2 |


## Out of scope (explicit non-goals)

These are pulldown-cmark extensions we explicitly don't port — see
[00_Goals.md](00_Goals.md#non-goals). Hooks exist at the option layer where they'd live; the
parser doesn't emit corresponding events:

- Definition lists
- Math (`$...$`, `$$...$$`)
- Wikilinks
- Metadata blocks (YAML / `+++`)
- Heading attributes (`# h { #id .class }`)
- Smart punctuation
- Superscript / subscript
- Old-footnote syntax
- Container extensions (`:::name`)
- Footnotes — design hooks present, but the parser doesn't currently emit `FootnoteReference` or
  `Tag::FootnoteDefinition` events. Adding them is a small, additive change (recognize `[^id]`
  in inline tokenization; recognize `[^id]:` at refdef-collection time).


## Known limitations beyond non-goals

- Multi-line refdefs with title on a third line work; some edge cases in the upstream Link
  reference definitions section (esp. ones interacting with raw HTML or empty labels) still fail.
- Pulldown's own `specs/table.txt` is a stricter suite than the GFM spec; we pass 4/29 there
  because most cases exercise interactions with constructs we don't implement.
- Forward-reference resolution in streaming mode degrades to `LinkType.*_UNKNOWN` /
  `BrokenLinkResolver`. Documented; oneshot's `prescan_refdefs=True` recovers full spec behavior.
- The single failing `gfm_table.txt` case (#5) involves a body row with no `|` that should still
  count as a row — our terminator rule closes the table on that line.
