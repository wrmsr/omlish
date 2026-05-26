# Investigation: pulldown-cmark internals

Notes from the initial read-through of the Rust crate at `pulldown-cmark/`, focused on what to port,
what to skip, and what informs our redesign for streaming.


## TL;DR

pulldown-cmark is a **two-pass, whole-document tree-backed parser** exposed via an `Iterator<Event>` API.
It is "pull" only from the consumer's perspective — the producer requires the entire input up front.
Its event surface is clean and stream-friendly and ports near-1:1 to Python. Its orchestration does not,
and we shouldn't try to mirror it. See [02_PrePlan.md](02_PrePlan.md) for the orchestration we will use
instead.


## Architecture, as it actually is

1. `Parser::new(text)` calls `firstpass::run_first_pass(text, options)`, which scans the **entire input**
   once and materializes a `Tree<Item>` (`tree.rs` — a vec-of-nodes with `child` / `next` links). This pass
   resolves block structure: paragraphs, headings, blockquotes, lists, code blocks, HTML blocks, tables,
   refdefs, footnote defs. Within each block it inserts placeholder nodes for "maybe-inline" candidates
   (`MaybeEmphasis`, `MaybeLinkOpen`, etc.).
2. `Iterator::next` (`parse.rs::next_event_range`) walks that tree in preorder. On first visit to a block,
   it runs the inline pass (`handle_inline_pass1` + `handle_emphasis_and_hard_break`) which resolves
   delimiter runs, links, code spans, math, autolinks, inline HTML — converting `Maybe*` placeholders into
   final inline nodes. Then it maps each `Item` to an `Event` via `item_to_event`.

So:

- The full document must be in memory.
- The full tree is built before any event is emitted.
- The iterator yields events lazily *over the already-built tree*; "lazy" here is about deferring inline
  resolution per block, not about feeding input incrementally.

This is fundamentally incompatible with chunked-input streaming, and no amount of "massaging" gets around
it. The two-pass design exists to handle constructs like reference link definitions and tight-vs-loose
list resolution that need whole-block context. We solve those differently — see PrePlan.


## Source layout (~14k LOC, ~9.8k excluding generated tables)

| file              | lines | role                                                                                  |
|-------------------|-------|---------------------------------------------------------------------------------------|
| `firstpass.rs`    | 2988  | block-structure pass; builds the tree; container/list/code/HTML/table/refdef scanners |
| `parse.rs`        | 2935  | tree types, inline pass, event emission, callbacks, refdef + footnote tables          |
| `scanners.rs`     | 1604  | byte-level scanners (LineStart, list markers, hrule, atx/setext, fences, autolinks)   |
| `puncttable.rs`   | 1541  | **generated** Unicode punctuation classifier — replaced by `unicodedata.category`     |
| `entities.rs`     | 2158  | **generated** HTML5 entity table — replaced by stdlib `html.entities` / `html.unescape` |
| `html.rs`         | 667   | reference HTML renderer driven by events; good template for our renderer              |
| `lib.rs`          | 778   | public API: `Tag`, `Event`, `Options`, `LinkType`, `Alignment`, `HeadingLevel`        |
| `strings.rs`      | 446   | `CowStr` / `InlineStr` — pure perf optimization, dropped                              |
| `tree.rs`         | 301   | vec-backed tree; obsolete given our single-pass model                                 |
| `linklabel.rs`    | 177   | case-insensitive link-label normalization for refdefs / footnotes                     |
| `utils.rs`        | 185   | `TextMergeStream` / `TextMergeWithOffset` (we mirror this)                            |


## Event API surface (ports cleanly)

The public event ADT maps directly to a sealed hierarchy of frozen dataclasses.

- `Event` variants: `Start(Tag)`, `End(TagEnd)`, `Text`, `Code`, `Html`, `InlineHtml`, `SoftBreak`,
  `HardBreak`, `Rule`, `TaskListMarker`, `FootnoteReference`, `InlineMath`, `DisplayMath`.
- `Tag` carries per-element data: `Heading{level,id,classes,attrs}`, `BlockQuote(kind?)`,
  `CodeBlock(Indented | Fenced(lang))`, `List(start_no?)`, `Item`, `Link/Image{type, url, title, id}`,
  `Table(alignments)`, `TableHead/Row/Cell`, `FootnoteDefinition(label)`, `DefinitionList/Title/Definition`,
  `MetadataBlock(kind)`, `ContainerBlock(kind, summary)`, `HtmlBlock`, and the span tags
  `Emphasis/Strong/Strikethrough/Superscript/Subscript`.
- `TagEnd` is a deliberately tiny copy of `Tag` (Rust mem-size optimization — there's a static assertion
  it stays ≤2 bytes). We have no equivalent constraint and can just carry an `EndTag` kind, or even reuse
  the Start tag's identity. PrePlan settles on a minimal `End(kind)` carrying just the discriminant plus
  any deferred-binding attributes (list tightness — see PrePlan §"Edge cases").
- `OffsetIter` yields `(Event, byte-range)` source-map pairs. We don't make this opt-in — every event
  carries its source offsets directly.
- `TextMergeStream` exists because the parser emits consecutive `Text` events freely (each text fragment
  is a slice of the source). We provide an equivalent `merge_text` utility.


## Feature surface (`Options` bitflags in `lib.rs`)

Roughly:

- **CommonMark core** (always on): paragraphs, atx + setext headings, blockquotes, fenced + indented code,
  ordered + bullet lists, thematic breaks, HTML blocks (7 types), inline HTML, link refs, autolinks,
  emphasis / strong, inline code, hard / soft breaks, backslash escapes, entities, images. **In our scope.**
- `ENABLE_TABLES` — GFM pipe tables with alignment row. **In our scope.**
- `ENABLE_STRIKETHROUGH` — `~~text~~`. **In our scope.**
- `ENABLE_TASKLISTS` — `- [x] checked` items. **In our scope.**
- `ENABLE_FOOTNOTES` (GFM) — `[^id]` references and `[^id]: …` definitions. **Stretch goal; punted.**
- `ENABLE_GFM` — only effect is `[!NOTE]` / `[!TIP]` / `[!IMPORTANT]` / `[!WARNING]` / `[!CAUTION]`
  admonition kinds on blockquotes. **Stretch goal; cheap if we want it.**
- `ENABLE_SMART_PUNCTUATION` — text substitution `--` `---` `...` `"…"` `'…'`. **Punted.**
- `ENABLE_MATH` — `$inline$` / `$$display$$`. **Punted.**
- `ENABLE_HEADING_ATTRIBUTES` — `# h { #id .cls a=b }`. **Punted.**
- `ENABLE_YAML_STYLE_METADATA_BLOCKS` / `ENABLE_PLUSES_DELIMITED_METADATA_BLOCKS`. **Punted.**
- `ENABLE_DEFINITION_LIST`, `ENABLE_SUPERSCRIPT`, `ENABLE_SUBSCRIPT`, `ENABLE_WIKILINKS`,
  `ENABLE_CONTAINER_EXTENSIONS`, `ENABLE_OLD_FOOTNOTES`. **All punted** — pulldown-specific or rare.

"Containers" in our spec means the CommonMark sense (blockquotes + lists), **not** pulldown's
`ContainerBlock` colon-fenced extension.


## What ports easily vs not

**Easy / direct ports:**

- Event / Tag ADTs → frozen dataclasses.
- Block-level scanners: atx, setext, hrule, code fence, blockquote marker, list marker, autolink,
  link destination, fence-close. These are byte-pattern functions and translate almost line-for-line.
- HTML entity decoding → drop the 2125-row generated table, use `html.unescape`.
- Unicode punctuation tests → drop the 1541-line generated table, use `unicodedata.category(c).startswith('P')`.
- HTML renderer (driven by events).
- `TextMergeStream`.

**Genuinely hard / spec-pinned:**

- **Inline emphasis / delimiter-run resolution.** `parse.rs::handle_emphasis_and_hard_break` with the
  `InlineStack` and its mod-3 `lower_bounds` trick is the subtlest piece of any CommonMark implementation.
  Algorithm is well-specified (CommonMark §6.2 / Appendix) but unforgiving and full of corner cases.
- **List parsing.** Tight vs loose, indent tracking, lazy continuation, list-vs-hrule disambiguation,
  sublists, marker continuity. The single hardest block-level construct.
- **HTML blocks.** Seven spec-defined types, each with its own start and end rules.
- **Reference link resolution.** Refdefs are accumulated; links resolve against them. Quadratic-blowup
  attack is real (the `link_ref_expansion_limit` exists for a reason); we replicate the fuel guard.

**Skipped / replaced wholesale:**

- The whole-document `Tree<Item>` representation and two-pass orchestration. We use a single-pass
  line-driven block parser with deferred per-block inline parsing instead.
- `CowStr` / `InlineStr` — just `str`.
- SIMD / `memchr` / `special_bytes` lookup tables — straightforward byte loops.
- Pulldown-specific extensions listed above.
- Broken-link / parser-callback machinery is replaced with one tidy hook (a `BrokenLinkResolver` protocol),
  matching pulldown's surface but not its generics-heavy plumbing.


## Streaming verdict

pulldown-cmark cannot be made to stream by patching. Three reasons, in order of severity:

1. `run_first_pass` consumes the entire input before returning. The tree it produces is the substrate
   the iterator walks; there is no "feed more bytes" entry point.
2. The tree is built with absolute byte offsets baked into every `Item`. Re-running the pass on a longer
   buffer would invalidate every offset and the iterator's notion of "current node".
3. Several decisions are made by post-passes on closed structures (e.g., `surgerize_tight_list`) which
   require the list to be fully built first.

The good news: the *event model* is naturally streaming-friendly even though the implementation isn't.
That's exactly what we exploit — we keep the API and re-do the orchestration. See
[02_PrePlan.md](02_PrePlan.md).


## Tests

`tests/suite/spec.rs` is auto-generated from `specs/*.txt`. Each `.txt` contains delimited examples in
`pre-formatted markdown / . separator / expected HTML` blocks. That format is portable, easy to ingest,
and is what we'll port for integration tests. Concretely we plan to port:

- A runner that reads `specs/*.txt`, runs parser → HTML, and diffs.
- The upstream CommonMark spec cases (the `spec` file is sourced from third-party `CommonMark/spec.txt`).
- `table.txt` and a representative subset of `regression.txt` covering the constructs we support.

We do not port `gfm_strikethrough.rs` / `gfm_tasklist.rs` etc. as Rust files — we wire their `.txt`
sources into our runner.


## Reference cross-walk (what to consult while implementing each piece)

| our concern             | pulldown-cmark files / functions to read                                      |
|-------------------------|-------------------------------------------------------------------------------|
| block state machine     | `firstpass.rs::FirstPass::{run, parse_block, parse_paragraph, parse_line}`    |
| containers (BQ + lists) | `firstpass.rs::{scan_containers, continue_list, finish_list, pop}`            |
| list markers            | `scanners.rs::LineStart::{scan_list_marker_with_indent, scan_task_list_marker}` |
| code fences             | `scanners.rs::{scan_code_fence, scan_closing_code_fence}`                     |
| HTML blocks             | `firstpass.rs::{parse_html_block_type_1_to_5, parse_html_block_type_6_or_7}`, `scanners.rs::{scan_html_block_inner, starts_html_block_type_6, scan_html_type_7}` |
| tables                  | `firstpass.rs::{parse_table, parse_table_row, parse_table_row_inner}`, `scanners.rs::scan_table_head` |
| setext headings         | `firstpass.rs::parse_setext_heading`, `scanners.rs::scan_setext_heading`      |
| refdefs                 | `firstpass.rs::{parse_refdef_label, parse_refdef_total, scan_refdef*}`        |
| inline emphasis         | `parse.rs::{handle_inline_pass1, handle_emphasis_and_hard_break, InlineStack}`, `delim_run_can_open`, `delim_run_can_close` |
| inline links / images   | `parse.rs::{handle_inline_pass1 (link branch), LinkStack, scan_reference}`    |
| code spans              | `parse.rs::{CodeDelims, make_code_span}`                                      |
| autolinks               | `scanners.rs::{scan_autolink, scan_uri, scan_email}`                          |
| inline HTML             | `scanners.rs::{scan_inline_html_*}`, `parse.rs::scan_inline_html`             |
| entities                | `scanners.rs::scan_entity`                                                    |
| HTML rendering          | `html.rs`                                                                     |
