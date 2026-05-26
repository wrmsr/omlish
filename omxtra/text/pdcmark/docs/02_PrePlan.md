# PrePlan: streaming model and parser shape

This document captures the design decisions reached before the formal implementation plan. It is the
contract the planner and implementation work against.

It depends on:

- [00_Goals.md](00_Goals.md) — the goals, non-goals, and cross-cutting invariants.
- [01_Investigation.md](01_Investigation.md) — what pulldown-cmark does internally and why we redesign
  the orchestration.


## Core decision: single-pass line-driven block parser with deferred per-block inline parsing

This is the architecture used by `cmark`, `commonmark.js`, and `markdown-it`. Unlike pulldown-cmark's
two-pass tree build, it composes naturally with chunked input. Sketch:

- A `BlockParser` owns a stack of open container blocks (root, blockquote, list, item) and at most one
  open leaf block (paragraph, heading, code block, HTML block, table, …).
- It also owns a line buffer for any incomplete trailing line and an absolute byte position counter.
- `feed(chunk)` appends the chunk to the line buffer, processes each newly newline-terminated line
  through the state machine (which may open / continue / close blocks), and at the end runs an inline
  pass over the currently-open block's accumulated text to produce the tentative tail.
- When a block closes, an inline pass runs over its final text and committed inline events are emitted.

The cost per `feed()` is bounded by **the size of the currently open block**, not the document. Codex's
controller re-renders the entire document on each newline; we don't.


## The streaming API

```python
@dc.dataclass(frozen=True)
class FeedOutput:
    committed: ta.Sequence[Event]    # newly committed since last feed; consumer APPENDS to stable log
    tentative: ta.Sequence[Event]    # current tail in full; consumer REPLACES its prior tentative

class StreamingParser:
    def feed(self, chunk: str) -> FeedOutput: ...
    def finish(self) -> FeedOutput: ...
```

Semantics:

- `feed(chunk)` consumes `chunk` (any string, including across-line / mid-word). Returns newly committed
  events and the full current tentative tail.
- `feed("")` is a no-op — returns `committed=[], tentative=<same as previous>`. We are not at the IO
  layer; empty string is not EOF.
- `finish()` signals end of input. Drains all tentative state into committed. After `finish()`, the
  parser is terminal and may not be fed again. (We will probably make this enforced — `RuntimeError` on
  post-`finish()` `feed`.)
- Non-streaming convenience: `parse(text: str) -> list[Event]` is implemented as
  `feed(text).committed + finish().committed`.

The two enforced invariants (cf. [00_Goals.md](00_Goals.md#cross-cutting-invariants)):

1. Once an event lands in `committed`, it is final.
2. `concat(all committed so far, current tentative)` equals what an oracle running on the prefix-of-input
   seen so far would produce.

And the strong guarantee:

3. `StreamingParser().feed(full_text).committed + finish().committed`
   == `StreamingParser().feed(chunk_1).committed + feed(chunk_2).committed + ... + finish().committed`
   for any chunking of `full_text`. **Chunking has zero observable effect on the final committed stream.**


## What is "committed" vs "tentative"

The general rule:

- A **block-start** event commits when its containing block has been unambiguously identified.
- **Block-content** events inside a leaf block commit at **block-close**, with one exception below.
- A **block-end** event commits at block-close.
- Everything else — the in-flight leaf block, plus any ambiguity not yet resolved — is **tentative**.

The exception: **opaque-content blocks** (fenced code blocks, indented code blocks, HTML blocks) commit
content line-by-line, because once a complete line is inside an unambiguous code/HTML block, no later
context can reinterpret it. Within such a block, only the *partial trailing line* is tentative. This is
what lets a multi-minute-long code block stream visibly without buffering everything.

Concretely, the tentative region is always a contiguous suffix of the current event stream and consists
of:

- Inline events from the currently open paragraph / heading / table cell, *or*
- The partial trailing line of an open code / HTML block, *or*
- Any lookahead-pending start events (e.g., a paragraph whose interpretation as setext heading or table
  header is not yet resolved).


## Edge cases that shape the state machine

These five are where the model is tested. Each is solved by keeping the relevant region in tentative
until disambiguated; none of them require retraction of committed events.

### Setext heading lookahead

A paragraph line is ambiguous: blank line / interrupt → paragraph; following `===` or `---` → setext
heading. The opened paragraph's `Start` and inline events stay tentative until the next line is seen.
On `===` / `---`, the tentative paragraph is replaced with a heading interpretation; on anything else,
the paragraph events commit. This is built into the block step, not the streaming API.

### Tables

A `| a | b |` line by itself is tentative as a paragraph. The next line either matches a GFM alignment
row (`| - | - |`) → retract tentative paragraph, commit as `Start(Table)` + `Start(TableHead)` + cells,
or doesn't → commit as paragraph and continue. This is the same mechanism that Codex's
`TableHoldbackScanner` implements externally; we get it for free.

### Reference link definition forward references

CommonMark allows `[a][b]` to reference `[b]: url` defined later. We don't do this in streaming. When
inline parsing runs at block-close time, only refdefs already seen exist. Unresolvable refs become
`LinkType.ReferenceUnknown` and go through a `BrokenLinkResolver` hook (matching pulldown-cmark's
surface but simpler — no callback generics).

For the oneshot `parse(text)` entry point, we may expose a `prescan_refdefs=True` option that does a
quick first-pass refdef scan to recover full spec compliance. Default `False`; documented as the
streaming / oneshot difference. **This is the only place we accept divergence from the spec.**

### List tight vs loose

A list is "loose" iff any item is separated from the next item by a blank line, or any item contains a
blank line between its blocks. This decision is end-of-list information.

Resolution: emit list-item content as paragraph events **always** (i.e., we don't emit a
`TightParagraph` variant at item time). The `End(List)` event carries a final `tight: bool` attribute.
The HTML renderer (and any other renderer) consults this at `End(List)` time to decide whether to
suppress `<p>` wrappers. Item events stay normal frozen events; tightness is a **late-binding attribute
on the list's end event**, not a retraction.

### Long-running open blocks (e.g., a 2-minute code fence)

Inside a fenced code block, each newline-terminated line is committable as a `Text` event — code text
is opaque. So the stream is `Start(CodeBlock, lang)` (committed once we've seen ```` ```lang ````
followed by a newline), then committed `Text` per line, then a single tentative `Text` for the
incomplete trailing line. `End(CodeBlock)` commits at close fence or `finish()`. The user sees output
arrive line-by-line; the tentative tail stays bounded.

This same pattern applies to indented code blocks and to HTML blocks.


## Events: surface and offsets

We follow pulldown-cmark's event surface (modulo the punted extensions) with these adaptations:

- **Source offsets are first-class on every event**, not opt-in via a separate iterator. Offsets are
  `(start, end)` byte positions into the absolute concatenated input stream.
- **Frozen dataclasses, not enums.** Each event variant is a small frozen dataclass; common base class
  for `isinstance` discrimination. The `Tag` union is similarly a hierarchy of frozen dataclasses.
- **`End` events are minimal.** A single `End` carrying the discriminant + any deferred-binding
  attributes. Concretely: `End(EndKind, list_tight: bool | None = None)` or equivalent. No mirrored copy
  of the start tag's payload.
- **Text events may be split.** Consecutive `Text` events from the parser are allowed; consumers that
  want a single concatenated text per inline span use a `merge_text(iter)` helper.
- **`Code`, `InlineHtml`, `Html`, `SoftBreak`, `HardBreak`, `Rule`, `TaskListMarker`,
  `FootnoteReference`** all map directly. `InlineMath` / `DisplayMath` are skipped (math is punted).


## Internal architecture sketch

Roughly four layers, hexagonal-ish. Names are tentative.

```
+----------------------------------------------+
|                StreamingParser               |   public surface
|     feed() / finish() / FeedOutput           |
+----------------------------------------------+
|                BlockMachine                  |   line-driven state machine
|   open container stack + open leaf block     |
|   advance(line) → committed[], updates       |
+----------------------------------------------+
|                InlineParser                  |   delimiter-run / link / code-span resolution
|   parse(text, refdefs, offset_base)          |
|   → list[Event]                              |
+----------------------------------------------+
|                  Scanners                    |   stateless byte-level pattern recognizers
|   scan_atx_heading, scan_code_fence,         |
|   scan_list_marker, scan_table_head, ...     |
+----------------------------------------------+
```

Each layer holds only the state it owns. Scanners are pure functions. `InlineParser` holds no
cross-block state. `BlockMachine` holds all the mutable parsing state (container stack, current leaf,
refdefs table, link-ref expansion fuel). `StreamingParser` holds the line buffer, absolute byte
position, and the previous tentative for nothing-changed deduping.

Module layout (target — final names settled in the formal plan):

- `pdcmark/__init__.py` — public re-exports.
- `pdcmark/events.py` — `Event` / `Tag` / `EndTag` / `LinkType` / `Alignment` / `HeadingLevel` dataclasses.
- `pdcmark/options.py` — `Options` config dataclass (frozen, defaults).
- `pdcmark/scanning/` — package of small modules per scanner family (lines, fences, lists, html, tables,
  links, autolinks, entities).
- `pdcmark/blocks/` — block state machine, container stack, leaf blocks. One small module per concern.
- `pdcmark/inlines/` — inline parser, delimiter stack, link resolver.
- `pdcmark/streaming/` — `StreamingParser` + `FeedOutput`.
- `pdcmark/parsing.py` — non-streaming `parse(text)` convenience.
- `pdcmark/rendering/html.py` — reference HTML renderer driven by events.
- `pdcmark/tests/` — tests, including the `.txt`-spec runner.

This errs on the side of small modules per CODESTYLE.md.


## DoS / resource bounds (mirror pulldown-cmark's)

- Nested-paren depth in link destinations: `LINK_MAX_NESTED_PARENS = 32`.
- Link-ref expansion fuel: at least 100 KiB plus input length, decremented on each link expansion.
  Beyond fuel, links become broken (callback may still resolve).
- Container nesting depth cap: 32 (blockquotes + lists combined). Pulldown's effective bound is similar
  in practice.
- Math brace nesting: irrelevant — math is punted.

These match pulldown's defaults. We expose them through `Options` for tuning. Default-on.


## Out of scope for this PrePlan

- AST layer (separate later module, driven solely from event stream).
- HTML rendering details beyond "exists and is event-driven".
- Renderer for the TUI use case (lives in the embedding project, not here).
- Exact dataclass field names / signatures — those land in the formal plan.
- Test-runner spec format details — those land with the implementation milestone for tests.


## Open questions deferred to the formal plan

1. Exact module names and `__init__.py` re-export shape.
2. Public surface of `BrokenLinkResolver` (protocol vs concrete dataclass strategy).
3. Whether `feed` returns a real frozen `FeedOutput` dataclass or destructures via tuple — going with
   the dataclass for self-documenting field names.
4. Iterator-style sugar: do we also expose `parser.events() -> Iterator[Event]` that yields committed
   events as they arrive, blocking until input is exhausted? Cheap convenience; defer to plan.
5. Whether `Options` is a `dc.dataclass` or a flag enum. Probably dataclass — better for IDE
   discoverability and we can pre-package CommonMark / GFM presets.
