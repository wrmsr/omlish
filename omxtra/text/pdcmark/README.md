# pdcmark

A pure-Python, streaming-first markdown parser modeled on the Rust
[`pulldown-cmark`](https://github.com/pulldown-cmark/pulldown-cmark) crate.

- Pure Python — no native extensions, no compiled dependencies.
- Zero runtime deps outside the `omcore` stdlib.
- Event-driven, with a `StreamingParser` that accepts chunked input and exposes both a committed (append-only,
  immutable) and tentative (replaceable) event stream — designed for live-rendering LLM TUIs without "safety reparse at
  end" passes.
- CommonMark core + GFM tables, strikethrough, task lists, and admonition blockquotes.
- Source offsets on every event.

Origin and design context: [docs/00_Goals.md](../docs/00_Goals.md),
[docs/02_PrePlan.md](../docs/02_PrePlan.md), [docs/03_Plan.md](../docs/03_Plan.md).


## Install

It ships as part of the parent project; from this repo:

```sh
python -m pip install -e .
```


## Quick start — oneshot parse

```python
import pdcmark

events = pdcmark.parse('# Hello\n\nA *paragraph*.\n')
for ev in events:
    print(ev)

# Or render to HTML:
from pdcmark.rendering.html import render_html
print(render_html(events))
```


## Streaming

For incremental input (LLM output, network streams), use `StreamingParser`. Each `feed(chunk)` returns a `FeedOutput`
with two parts:

- **`committed`** — events newly finalized since the last call. Append these to a stable log; they will never change.
- **`tentative`** — the parser's current best guess for what would emit if input ended right now. Replace your previous
  tentative with this on each call.

```python
import pdcmark

sp = pdcmark.StreamingParser()

stable = []                            # consumer's append-only event log
tentative = []                         # consumer's mutable tail

for chunk in incoming_chunks:
    out = sp.feed(chunk)
    stable.extend(out.committed)
    tentative = list(out.tentative)
    render(stable, tentative)          # consumer redraws

out = sp.finish()
stable.extend(out.committed)
tentative = []
render(stable, tentative)
```

### Guarantees

The streaming and oneshot modes share the same parser. Concretely:

> For any chunking of `text`, the concatenated `committed` stream from
> `feed()`-then-`finish()` equals `parse(text)`.

This is verified by `pdcmark/tests/test_streaming/test_equivalence.py` over the full upstream CommonMark spec corpus
plus the GFM extension fixtures, under 8 chunking strategies (whole, each-char, fixed-size, by-line, random). The
consumer never needs to re-render from scratch "just to be safe".

`feed("")` is an explicit no-op (returns committed `()` and the unchanged tentative). After `finish()`, the parser is
terminal — further `feed()` calls raise `ParserStateError`.


## Events

All events are immutable frozen dataclasses. Every event carries `offset: tuple[int, int]` —
character indices into the absolute input stream.

| Event class | Notes |
|---|---|
| `Start(tag: Tag)` / `End(tag: Tag)` | Open/close a tagged element. |
| `Text(text)` | Literal text content (may be split into multiple consecutive events — see `merge_text`). |
| `Code(text)` | Inline code span (verbatim text). |
| `Html(text)` / `InlineHtml(text)` | Raw HTML — block-level and inline respectively. |
| `SoftBreak` / `HardBreak` | Line breaks inside a paragraph. |
| `Rule` | Thematic break (`<hr/>`). |
| `TaskListMarker(checked: bool)` | GFM task-list `[x]` marker. |

The `Tag` hierarchy mirrors pulldown-cmark's: `Paragraph`, `Heading(level)`, `BlockQuote(kind?)`,
`FencedCodeBlock(info)` / `IndentedCodeBlock`, `HtmlBlock`, `List(start?, tight?)` / `Item`,
`Table(alignments)` / `TableHead` / `TableRow` / `TableCell`, `Emphasis` / `Strong` /
`Strikethrough`, `Link(...)` / `Image(...)`.

`List.tight` is set on the `End(List)` event only — see the tight/loose handling in
[docs/03_Plan.md](../docs/03_Plan.md#event--tag-dataclass-shapes). The HTML renderer reads it from there to decide
whether to wrap items' content in `<p>`.


## Options

```python
import pdcmark
from omcore import dataclasses as dc

opts = dc.replace(
    pdcmark.COMMONMARK,
    tables=True,
    strikethrough=True,
    tasklists=True,
    prescan_refdefs=True,             # oneshot only — collect refdefs in a pre-pass
)

# Or use a preset:
events = pdcmark.parse(text, pdcmark.GFM)
```

Notable knobs:

- `tables`, `strikethrough`, `tasklists`, `gfm_blockquote_kinds` — enable the corresponding GFM extensions.
- `prescan_refdefs` — oneshot mode only. Runs a discarded first pass to populate the refdef table so links can resolve
  against refdefs defined later in the document. Ignored by `StreamingParser` (streaming has no lookahead — forward refs
  become `LinkType.*_UNKNOWN` and go through `broken_link_resolver`).
- `broken_link_resolver: BrokenLinkResolver | None` — callback for unresolved reference links.
- `max_nested_parens`, `max_container_depth`, `link_ref_expansion_min` — DoS-mitigation bounds.


## Reference link resolution

Reference link definitions (`[label]: dest "title"`) are collected as paragraphs close. In streaming mode, only refdefs
seen before a link's containing block closes are visible to that link; forward references degrade to
`LinkType.*_UNKNOWN` and consult the `BrokenLinkResolver` callback (if any). For full spec-compliant forward-ref
resolution in oneshot mode, set `Options.prescan_refdefs=True`.

Link-expansion fuel guards against quadratic-blowup adversarial inputs (cf.
pulldown-cmark/src/parse.rs::ParserInner::link_ref_expansion_limit). The default budget is `max(len(input), 100_000)`
and is tunable via `Options.link_ref_expansion_min`.


## Spec compliance (current)

| Suite | Default | `prescan_refdefs=True` |
|---|---|---|
| CommonMark spec.txt | 459/572 | 503/572 (88%) |
| GFM strikethrough | 3/3 | — |
| GFM table | 8/9 | — |
| GFM tasklist | 2/2 | — |

The remaining gap is mostly pulldown-specific extensions we deliberately don't support (definition lists, math, metadata
blocks, heading attributes, wikilinks, container extensions, old-footnote syntax) and a handful of multi-line refdef +
raw-HTML edge cases.


## Project layout

```
pdcmark/
  events.py                # Event / Tag hierarchy
  options.py               # Options + COMMONMARK / GFM presets
  brokenlinks.py           # BrokenLinkResolver protocol
  errors.py                # exception hierarchy
  parsing.py               # oneshot parse()
  scanning/                # stateless byte-level scanners
  blocks/                  # block-state machine
  inlines/                 # inline parser (tokenize → resolve_links → resolve_emphasis → events)
  streaming/               # StreamingParser + FeedOutput
  rendering/html.py        # event-driven HTML renderer
  utils/text_merge.py      # merge_text helper
  tests/                   # unit tests, spec-runner integration, streaming equivalence
```


## Acknowledgments

This is a port of [pulldown-cmark](https://github.com/pulldown-cmark/pulldown-cmark) — the Rust crate's event surface
and individual byte-level scanners served as the reference throughout. Cross-reference comments on most non-trivial
helpers point back to specific files / functions in the upstream codebase.
