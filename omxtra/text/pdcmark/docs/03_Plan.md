# Plan: implementation strategy and milestones

This document is the concrete plan. It builds on [00_Goals.md](00_Goals.md),
[01_Investigation.md](01_Investigation.md), and [02_PrePlan.md](02_PrePlan.md).

Surface-level design decisions are locked in — see [Decisions locked in](#decisions-locked-in) at the
bottom for the summary.


## Sequencing principle

Bottom-up, each milestone leaving the code in a tested, useful state.

- **The block state machine is built from day one with a `feed_line(line)` entry point**, not a
  whole-text loop. Oneshot `parse(text)` calls `feed_line` per line internally; the streaming layer
  added later wraps it with chunk → line buffering. Streaming is a thin wrapper around an already
  streaming-shaped core, not a retrofit.
- **Every milestone ends with green spec-runner tests** for the constructs it adds. We are not
  shipping unreviewed code between milestones.
- **Inline parsing is per-block and stateless across blocks.** No cross-block inline state. This makes
  the per-feed cost bounded by the open block's size (see [02_PrePlan.md](02_PrePlan.md#why-this-is-cheaper-than-codexs-rebuild-on-every-delta)).


## Module layout

Final names. Small modules; structure mirrors the layer diagram in PrePlan.

```
pdcmark/
  __init__.py                # public re-exports
  events.py                  # Event / Tag dataclass hierarchies; LinkType; Alignment
  options.py                 # Options dataclass + presets (CommonMark, GFM)
  errors.py                  # exceptions (ParseError, BrokenLinkError if used)
  brokenlinks.py             # BrokenLinkResolver protocol + default no-op impl

  scanning/                  # stateless byte-level scanners (pure functions / dataclass returns)
    __init__.py
    lines.py                 # LineStart equivalent (indent/whitespace tracking)
    whitespace.py            # is_ascii_whitespace, scan_blank_line, scan_eol, ...
    atx.py                   # ATX heading scan
    setext.py                # setext underline scan
    hrule.py                 # thematic break scan
    fences.py                # fenced code block open/close
    indented.py              # indented code block detection
    blockquotes.py           # blockquote marker scan
    lists.py                 # list marker scan, task list marker scan
    html_blocks.py           # 7 HTML block types
    tables.py                # table head row, alignment row, body row parsing
    inline_html.py           # inline HTML (tag, comment, processing, declaration, CDATA)
    autolinks.py             # autolink, email autolink
    links.py                 # link destination, link title, link label
    entities.py              # numeric + named entity scan (uses html.unescape)
    escapes.py               # backslash escape table

  blocks/                    # block state machine
    __init__.py
    machine.py               # BlockMachine: stack + feed_line + flush
    stack.py                 # container stack representation
    containers.py            # blockquote, list, item container types
    leaves.py                # paragraph, heading, code block, html block, table leaf types
    refdefs.py               # reference link definition table
    tightness.py             # list tight/loose tracking

  inlines/                   # per-block inline parser
    __init__.py
    parser.py                # InlineParser: text → list[Event]
    delimiters.py            # delimiter stack, run open/close classification
    emphasis.py              # emphasis/strong resolution (delimiter run algorithm)
    code_spans.py            # backtick code span resolution
    links.py                 # link/image resolution + ref expansion fuel
    autolinks.py             # autolink resolution wrapper
    escapes.py               # backslash + entity application to text

  streaming/
    __init__.py
    output.py                # FeedOutput dataclass
    parser.py                # StreamingParser: chunk buffer + BlockMachine driver

  parsing.py                 # oneshot parse(text) -> list[Event]

  rendering/
    __init__.py
    html.py                  # event-driven HTML renderer

  utils/
    __init__.py
    text_merge.py            # merge consecutive Text events

  tests/
    __init__.py
    conftest.py
    spec_runner.py           # parses .txt spec files, drives parse + render, diffs
    data/                    # ported .txt spec files (commonmark, table, regression subset)
    test_scanners/           # unit tests per scanner family
    test_blocks/             # block state machine tests
    test_inlines/            # inline parser tests
    test_streaming/          # chunked-input equivalence tests
    test_render/             # html renderer tests
    test_spec_*              # spec-runner-driven integration tests
```


## Public API surface

What downstream code imports. Everything else is private implementation detail.

```python
from pdcmark import (
    # parser entry points
    parse,                   # oneshot: (text: str, options: Options = COMMONMARK) -> list[Event]
    StreamingParser,         # streaming
    FeedOutput,              # streaming result

    # options
    Options,
    COMMONMARK,              # Options preset
    GFM,                     # Options preset

    # events
    Event,
    Start, End, Text, Code, Html, InlineHtml,
    SoftBreak, HardBreak, Rule, TaskListMarker,

    # tags
    Tag,
    Paragraph, Heading, BlockQuote,
    FencedCodeBlock, IndentedCodeBlock, HtmlBlock,
    List, Item,
    Table, TableHead, TableRow, TableCell,
    Emphasis, Strong, Strikethrough,
    Link, Image,

    # enums / value types
    LinkType, Alignment, BlockQuoteKind,

    # extension hooks
    BrokenLinkResolver,
)
from pdcmark.rendering.html import render_html
from pdcmark.utils.text_merge import merge_text
```


## Event / Tag dataclass shapes

```python
# events.py (sketch)

import typing as ta
from omcore import dataclasses as dc
from omcore import lang


class LinkType(enum.Enum):
    INLINE = 'inline'
    REFERENCE = 'reference'
    REFERENCE_UNKNOWN = 'reference_unknown'
    COLLAPSED = 'collapsed'
    COLLAPSED_UNKNOWN = 'collapsed_unknown'
    SHORTCUT = 'shortcut'
    SHORTCUT_UNKNOWN = 'shortcut_unknown'
    AUTOLINK = 'autolink'
    EMAIL = 'email'


class Alignment(enum.Enum):
    NONE = 'none'
    LEFT = 'left'
    CENTER = 'center'
    RIGHT = 'right'


class BlockQuoteKind(enum.Enum):
    NOTE = 'note'
    TIP = 'tip'
    IMPORTANT = 'important'
    WARNING = 'warning'
    CAUTION = 'caution'


##  Tags  ##

@dc.dataclass(frozen=True)
class Tag(lang.Abstract):
    pass

@dc.dataclass(frozen=True)
class Paragraph(Tag):
    pass

@dc.dataclass(frozen=True)
class Heading(Tag):
    level: int  # 1..6

@dc.dataclass(frozen=True)
class BlockQuote(Tag):
    kind: BlockQuoteKind | None = None  # GFM admonition; None = regular

@dc.dataclass(frozen=True)
class FencedCodeBlock(Tag):
    info: str  # may be empty

@dc.dataclass(frozen=True)
class IndentedCodeBlock(Tag):
    pass

@dc.dataclass(frozen=True)
class HtmlBlock(Tag):
    pass

@dc.dataclass(frozen=True)
class List(Tag):
    start: int | None = None    # None = unordered
    tight: bool | None = None   # None at Start; bool at End (see "list tightness" below)

@dc.dataclass(frozen=True)
class Item(Tag):
    pass

@dc.dataclass(frozen=True)
class Table(Tag):
    alignments: ta.Sequence[Alignment]

@dc.dataclass(frozen=True)
class TableHead(Tag):
    pass

@dc.dataclass(frozen=True)
class TableRow(Tag):
    pass

@dc.dataclass(frozen=True)
class TableCell(Tag):
    pass

@dc.dataclass(frozen=True)
class Emphasis(Tag):
    pass

@dc.dataclass(frozen=True)
class Strong(Tag):
    pass

@dc.dataclass(frozen=True)
class Strikethrough(Tag):
    pass

@dc.dataclass(frozen=True)
class Link(Tag):
    link_type: LinkType
    dest_url: str
    title: str
    id: str

@dc.dataclass(frozen=True)
class Image(Tag):
    link_type: LinkType
    dest_url: str
    title: str
    id: str


##  Events  ##

@dc.dataclass(frozen=True)
class Event(lang.Abstract):
    offset: tuple[int, int]  # absolute byte range in the input stream

@dc.dataclass(frozen=True)
class Start(Event):
    tag: Tag

@dc.dataclass(frozen=True)
class End(Event):
    tag: Tag

@dc.dataclass(frozen=True)
class Text(Event):
    text: str

@dc.dataclass(frozen=True)
class Code(Event):
    text: str

@dc.dataclass(frozen=True)
class Html(Event):
    text: str

@dc.dataclass(frozen=True)
class InlineHtml(Event):
    text: str

@dc.dataclass(frozen=True)
class SoftBreak(Event):
    pass

@dc.dataclass(frozen=True)
class HardBreak(Event):
    pass

@dc.dataclass(frozen=True)
class Rule(Event):
    pass

@dc.dataclass(frozen=True)
class TaskListMarker(Event):
    checked: bool
```

Notes:

- `Tag` is a `lang.Abstract` marker base. No methods. Pure data. Same shape for every "capability"
  marker class throughout the codebase — empty abstract base over union types — as a project-wide
  preference (we want `isinstance(t, Tag)` to mean something).
- `Start` and `End` both carry the same `tag` instance type. Pattern matching is uniform:
  `match event: case End(tag=List(tight=tight)): ...`.
- **List tightness lives on the `List` tag itself**, with a `None` sentinel at `Start` time and a
  `bool` set at `End` time. The renderer reads it off `End(tag=List(tight=...))`. This puts
  tightness conceptually where it belongs (a property of the list, not of the End event), keeps
  `End` minimal, and scales cleanly: any future deferred-binding attribute lives as a sentinel
  field on its own tag rather than accreting onto `End`.
- We don't emit pulldown's `TightParagraph` distinction. Items always contain `Paragraph` events;
  the HTML renderer buffers per-list and, at `End(List)`, suppresses `<p>` wrappers if
  `tight=True`. (Analogous to `parse.rs::surgerize_tight_list` rewriting the tree post-pass — but
  done at render time on a buffered event window, not by mutating shared state.)


## Options shape

```python
# options.py (sketch)

@dc.dataclass(frozen=True, kw_only=True)
class Options:
    # extensions
    tables: bool = False
    strikethrough: bool = False
    tasklists: bool = False
    gfm_blockquote_kinds: bool = False  # [!NOTE] etc.

    # bounds (DoS mitigation; mirror pulldown-cmark's defaults — see src/parse.rs)
    max_nested_parens: int = 32          # LINK_MAX_NESTED_PARENS in src/parse.rs
    max_container_depth: int = 32
    link_ref_expansion_min: int = 100_000  # plus len(input); ParserInner::link_ref_expansion_limit

    # streaming behavior
    prescan_refdefs: bool = False  # oneshot only; ignored by StreamingParser

    # broken link callback (cf. src/parse.rs::ParserCallbacks::handle_broken_link)
    broken_link_resolver: BrokenLinkResolver | None = None


COMMONMARK = Options()
GFM = dc.replace(
    COMMONMARK,
    tables=True,
    strikethrough=True,
    tasklists=True,
    gfm_blockquote_kinds=True,
)
```

All configuration-shaped dataclasses (anything resembling injected options or a result aggregate) are
`kw_only=True`. `FeedOutput` is also `kw_only=True`. Event / Tag dataclasses are positional — they
are constructed densely in the parser and the field order is meaningful.


## Internal architecture boundaries

All `feed_*` / `parse` / `finish` entry points return **materialized `list[Event]`**, not
generators. The streaming layer's tentative-rebuild requires repeated re-parse of the open block on
every chunk, and several constructs (tables, refdefs, list tightness) need whole-block context
before any event can be emitted — i.e. we are effectively eager per block regardless. Locking that in
explicitly avoids the generator-overhead-without-the-streaming-benefit failure mode and keeps results
indexable / debuggable. "Streaming" lives at the chunk → committed-events boundary, not at the
event-iteration boundary.

### Scanners (`pdcmark/scanning/`)

Pure functions over byte buffers. No state. Each returns either an `int` (bytes consumed, `0` for no
match) or a small frozen result dataclass (`AtxHeadingMatch`, `FenceMatch`, …) with the parsed data
and bytes consumed.

```python
# pulldown-cmark/src/scanners.rs::scan_atx_heading
def scan_atx_heading(line: bytes) -> AtxHeadingMatch | None: ...

# pulldown-cmark/src/scanners.rs::scan_code_fence
def scan_fenced_code_open(line: bytes) -> FenceOpenMatch | None: ...
```

These are the moral equivalent of pulldown-cmark's `scanners.rs` and the inner scanners of
`firstpass.rs`, ported to Python. They are independently unit-testable.

### `BlockMachine` (`pdcmark/blocks/machine.py`)

Closest rust analogue: `pulldown-cmark/src/firstpass.rs::FirstPass`. Same line-driven model and same
container-stack semantics, but exposed as an explicit `feed_line(line)` state machine rather than a
private struct driven by a single `run()` loop — and we do **not** build a `Tree<Item>`. Events are
emitted at block close instead of accumulated in a tree the iterator walks later.

```python
class BlockMachine:
    def __init__(self, options: Options): ...

    def feed_line(self, line: str, offset: int) -> list[Event]:
        """Process one complete line (without trailing newline preserved in the data) starting at
        absolute byte position `offset`. Returns events that became committed as a result."""

    def tentative_events(self) -> list[Event]:
        """Inline-parse the currently open leaf block's buffered text and return the events that
        would be emitted if input ended right now (but did not close pending blocks)."""

    def finish(self, offset: int) -> list[Event]:
        """Close all open blocks; return remaining events. Machine is terminal after this."""
```

State:

- Stack of open containers (root, blockquote, list, item).
- At most one open leaf block (paragraph buffer, code-block lines, etc.).
- Reference link definition table (`pulldown-cmark/src/parse.rs::RefDefs`).
- Link-ref expansion fuel counter (`pulldown-cmark/src/parse.rs::ParserInner::link_ref_expansion_limit`).
- List-tightness tracking per active list (cf. `pulldown-cmark/src/parse.rs::surgerize_tight_list`).

The state machine is **mutable**; events it returns are **immutable**.

### `InlineParser` (`pdcmark/inlines/parser.py`)

Closest rust analogue: `pulldown-cmark/src/parse.rs::{handle_inline_pass1, handle_emphasis_and_hard_break}`.
Same per-block delimiter-stack model, but invoked as a self-contained `parse(text)` over a complete
block instead of as a tree mutation pass.

```python
class InlineParser:
    def __init__(self, options: Options, refdefs: RefDefs, fuel: Fuel): ...

    def parse(self, text: str, base_offset: int) -> list[Event]:
        """Inline-parse a complete block's text. Stateless across calls."""
```

Takes refdefs and the fuel counter (a small mutable container) by reference. Has no other state — a
fresh delimiter stack is built per call. This matters: it means `tentative_events()` can call
`parse()` on the open block's current buffer cheaply and repeatedly without polluting state.

### `StreamingParser` (`pdcmark/streaming/parser.py`)

```python
class StreamingParser:
    def __init__(self, options: Options = COMMONMARK): ...

    def feed(self, chunk: str) -> FeedOutput: ...

    def finish(self) -> FeedOutput: ...
```

State:

- A `BlockMachine` instance.
- Line buffer for incomplete trailing line.
- Absolute byte position (advanced per consumed character).
- Previous tentative tail (for re-emission as-is — required by "strict re-emit" semantics from the
  PrePlan).
- A terminated flag (so post-`finish()` `feed()` raises).

`feed()` algorithm:

1. If chunk is empty, return `FeedOutput([], previous_tentative)`.
2. Append chunk to buffer. Find newlines.
3. For each complete line, call `block_machine.feed_line(line, line_offset)`. Collect committed
   events.
4. After all complete lines processed, run `block_machine.tentative_events()` plus an extra inline
   parse over the partial trailing line buffer if relevant.
5. Cache the new tentative; return `FeedOutput(committed, tentative)`.

### `render_html` (`pdcmark/rendering/html.py`)

Single function `render_html(events: ta.Iterable[Event]) -> str`. Buffers per-list to apply
`list_tight` at `End(List)` time. Otherwise straight transcription.


## Implementation milestones

Each milestone exits with passing tests on the constructs it adds, no failing tests anywhere, and a
self-contained working state.

### M0 — Skeleton, events, options, test scaffolding

- `events.py`, `options.py`, `errors.py`, `brokenlinks.py` (with default no-op resolver).
- `tests/spec_runner.py` skeleton that reads `.txt` spec format and runs configurable
  `parse + render` pipelines. Stub a few simple tests against a placeholder no-op parser.
- `utils/text_merge.py` ported.
- Package layout, `__init__.py` re-exports, conftest.
- **Exit criteria:** module imports clean, dataclasses construct, spec runner finds and parses
  example blocks correctly. Zero parsing logic yet.

### M1 — Block state machine: CommonMark core blocks (no inline parsing yet)

- All block scanners in `pdcmark/scanning/` ported and unit-tested.
- `BlockMachine` with: paragraphs, ATX + setext headings, thematic breaks, fenced + indented code
  blocks, HTML blocks (all 7 types), blockquotes, lists (including nested and lazy continuation,
  *without* tight/loose).
- Reference link definitions detected and stored (resolution deferred to M3).
- Inline phase emits raw `Text` events only (no emphasis, no links, no entities).
- HTML renderer M1 subset.
- `parse(text)` works for pure-block fixtures.
- **Exit criteria:** spec runner passes block-only CommonMark spec cases (those without inline
  emphasis / links). Setext headings, lazy blockquote continuation, list-vs-hrule disambiguation
  all green.

### M2 — Inline parsing (core)

- `InlineParser` with: backslash escapes, entity references, code spans, autolinks, inline HTML,
  hard / soft breaks, emphasis / strong (delimiter run algorithm).
- HTML renderer extended for new events.
- **Exit criteria:** CommonMark spec inline cases (other than links/refs) green. Delimiter-run
  corner cases (mod-3 rule, intraword underscore, mixed emphasis) covered by unit tests.

### M3 — Links, images, refdefs

- Full link / image resolution: inline, reference, collapsed, shortcut, and `*_UNKNOWN` variants.
- Link expansion fuel guard.
- `BrokenLinkResolver` hook used when a ref doesn't resolve.
- Streaming mode: forward refs become `*_UNKNOWN` (the punt we documented).
- Optional `prescan_refdefs=True` flag on oneshot `parse()` for spec-perfect link resolution.
- **Exit criteria:** CommonMark spec link/image cases green (with `prescan_refdefs=True` in oneshot
  mode). DoS fuel test passes (no exponential blowup on adversarial input).

### M4 — GFM extensions in scope: tables, tasklists, strikethrough

- Table parsing, including the "header row tentative until alignment row seen" pattern.
- Task list markers as the first inline element of a list item.
- Strikethrough (`~~text~~`) via the delimiter stack with `~` as a delimiter character.
- Optional GFM admonition `BlockQuoteKind` (cheap; behind `gfm_blockquote_kinds=True`).
- **Exit criteria:** GFM table spec cases green; tasklist + strikethrough cases green.

### M5 — List tightness

- Tight/loose detection per list during block parsing.
- `End(tag=List(...), list_tight=...)` emitted with the resolved value.
- Renderer suppresses `<p>` wrappers inside items when `list_tight=True`.
- **Exit criteria:** previously-deferred tight list cases now green.

### M6 — Streaming layer

- `StreamingParser`, `FeedOutput`.
- Chunk → line buffering.
- Open-block tentative emission via `BlockMachine.tentative_events()` (and partial-line re-inline-
  parse where applicable).
- Property tests: for randomized chunkings of fixture inputs, the concatenated committed stream
  equals the oneshot `parse(text)` output. **This is invariant #3 from the goals doc; it gets a
  dedicated test module.**
- Post-`finish()` `feed()` raises.
- **Exit criteria:** all M1-M5 spec cases also pass when fed in random chunkings.

### M7 — Polish

- `merge_text` utility tested.
- `text_offset` consistency tests (offsets monotonic, non-overlapping for non-Start/End events).
- README at `pdcmark/`.
- Docstrings on public surface where genuinely non-obvious.
- Stretch: footnotes if time/interest; otherwise documented as "design hooks present, parser doesn't
  emit yet."


## Testing strategy

Three layers:

1. **Unit tests per module** — `tests/test_scanners/`, `tests/test_blocks/`, `tests/test_inlines/`.
   Standard pytest. Fine-grained, fast, no rendering involved.
2. **Spec-runner integration tests** — `tests/data/*.txt` ported from `pulldown-cmark/specs/`. The
   runner parses one fixture file's example blocks, runs `parse + render_html`, diffs against
   expected. One pytest function per example, parameterized.
3. **Streaming equivalence tests** — `tests/test_streaming/`. For each fixture in (2), feed the
   input as N random chunkings and assert the concatenated committed stream equals the oneshot
   parse output. Hypothesis is a nice fit but `omlish` doesn't include it; we'll use a small
   deterministic chunker plus a random one seeded per test.

Spec fixture files we port (in order, milestone-aligned):

- M1: a curated subset of `commonmark.txt` covering only block-level cases.
- M2: the remainder of `commonmark.txt` minus links/refs.
- M3: the link / refdef portions of `commonmark.txt`.
- M4: `table.txt`, `gfm_strikethrough` cases, `gfm_tasklist` cases.
- M6: streaming equivalence runs over the union of the above.


## Out of scope for this plan

These are tracked separately when their time comes.

- AST layer over events (separate later module).
- TUI integration (lives in the embedding project).
- Footnotes (stretch; design hook only).
- Math / wikilinks / definition lists / metadata blocks / heading attrs / smart punctuation / sub /
  super / container extensions (all explicitly punted in 00_Goals.md).


## Code annotation: rust cross-references

Where Python code is recognizably analogous to a chunk of pulldown-cmark, we add a brief comment at
the definition citing the relative path under `pulldown-cmark/` and, if it differs in any meaningful
way, a short note on what's similar / different. We are not aiming for 1:1, and we don't gild every
single function — but for anything a reader would want to look up in the upstream codebase for
context, we leave a breadcrumb.

The pattern, schematically:

```python
# pulldown-cmark/src/scanners.rs::scan_atx_heading
def scan_atx_heading(line: bytes) -> AtxHeadingMatch | None:
    ...

# pulldown-cmark/src/firstpass.rs::FirstPass — same line-driven block model, but exposed via
# feed_line() rather than internal `run()`; no Tree<Item>.
class BlockMachine:
    ...
```

Conventions:

- The path is relative to the repo root (so it starts `pulldown-cmark/...`), no git rev. The
  submodule pin is the source of truth.
- The form is `<path>::<symbol>` to keep grep-friendly.
- One-line note iff the python diverges in a way that isn't obvious from the names. Skip the note if
  it's a near-direct port.
- Apply to: scanners, the block state machine, the inline parser's main entry points,
  delimiter-stack internals, HTML renderer entry points, and any structurally analogous helpers.
  Skip on trivial dataclasses and python-idiomatic glue with no rust counterpart.


## Decisions locked in

For posterity / so we don't relitigate later:

1. `Event` and `Tag` are `lang.Abstract` marker bases. Project-wide preference: empty abstract base
   over `TypeAlias = Union[…]` for capability markers.
2. List tightness lives as a `tight: bool | None` field on the `List` tag itself (`None` at Start,
   `bool` at End). `End` stays minimal. Future deferred-binding attributes follow the same pattern
   on their own tag.
3. `Options` is a frozen `kw_only=True` dataclass with `COMMONMARK` and `GFM` preset constants.
   `FeedOutput` is also `kw_only=True`. Event / Tag dataclasses stay positional.
4. HTML renderer lives in the `pdcmark/rendering/` subpackage.
5. `parse(text) -> list[Event]` returns a materialized list, eager. Same goes for `BlockMachine` /
   `InlineParser` entry points (see "Internal architecture boundaries" above). Streaming lives at
   the chunk → committed-events boundary, not at the event-iteration boundary.
6. Spec runner parameterizes pytest cases at import time via `pytest.mark.parametrize` populated
   from a function that walks each `.txt` fixture file. One python test ID per spec example.
