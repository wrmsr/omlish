# Goals

`pdcmark` is a pure-Python translation of [pulldown-cmark](https://github.com/pulldown-cmark/pulldown-cmark)
(the Rust CommonMark pull parser), redesigned around streaming.

The rust crate is checked out as a submodule at `pulldown-cmark/` and is used as a reference for the event API
surface and for individual byte-level scanners. We do **not** mirror its internal two-pass tree-based
orchestration — see [01_Investigation.md](01_Investigation.md) for why and [02_PrePlan.md](02_PrePlan.md) for
what we do instead.


## Goals

- **Pure Python.** No native extensions, no compiled deps.
- **Zero runtime dependencies** except the `omlish` stdlib (which is already installed and is the only thing
  the embedding project lets us depend on).
- **Event-driven / stream-native.** This is the load-bearing design constraint. The parser must accept input
  in arbitrary chunks (mid-line, mid-word) and emit incremental output as soon as it is structurally final,
  while also exposing a tentative tail so that a TUI can render not-yet-final content in real time. See
  [02_PrePlan.md](02_PrePlan.md) for the committed / tentative model.
- **Versatile and hackable.** Bias toward small, composable modules of frozen dataclasses (per `CODESTYLE.md`)
  over monolithic state.
- **Capable, or self-aware when it isn't.** Where we don't handle a feature, we degrade gracefully rather than
  crash or silently miscount.
- **Algorithmically careful.** We are self-aware about being pure Python and are not chasing raw throughput;
  but we do avoid quadratic-string-concat patterns, blow-up reparses, and the like.
- **Clean and well-structured.** Cluster of small frozen-dataclass modules, callee-before-caller flow,
  hexagonal-ish separation.


## Non-goals

- **Not feature-complete vs pulldown-cmark.** We support the CommonMark common subset plus tables and the
  CommonMark container blocks (blockquotes and lists). The pulldown-specific extensions
  (`ContainerKind::Spoiler`, math, definition lists, metadata blocks, wikilinks, super/subscript, heading
  attributes, smart punctuation, old footnotes) are out of scope for the initial version. The architecture
  should keep porting them later straightforward, but they aren't day-one.
- **Not fast.** We are self-awarely pure Python. The Rust crate's `CowStr`, `InlineStr`, SIMD scanners,
  `memchr`, and packed `ItemBody` discriminants exist for speed; we omit all of them.
- **Not a full test-suite port.** We port the integration-style spec runner and the upstream CommonMark spec
  cases plus a representative slice of the table / GFM regression files. We do not port the auto-generated
  ~160k-line `tests/suite/spec.rs`.
- **Not a hosted parse-state.** We do not provide fork / persistent-snapshot semantics. The parser is a
  single-owned mutable object; the events it emits are immutable.


## Primary use case

Replacement for `markdown-it-py` inside an LLM / TUI toolbox that hates external dependencies. Specifically:

- Long, streamed LLM responses rendered live into a TUI.
- The TUI maintains a "committed scrollback" of stable rendered lines and a mutable "tail" region that
  redraws on each delta. Today this is done by re-rendering the entire raw source on every chunk (see
  Codex's `codex-rs/tui/src/streaming/controller.rs` and `markdown_render.rs`). Our streaming model is
  designed so the consumer doesn't have to do that — see [02_PrePlan.md](02_PrePlan.md).


## Secondary use case

An optional AST layer built **solely from the event stream**. Not in the initial version, but the event
surface should be expressive enough to losslessly reconstruct a tree. The AST builder lives in a separate
module and the evented core knows nothing about it.


## Cross-cutting invariants

These are guarantees the implementation must uphold; they shape multiple parts of the design.

1. **Committed events are immutable and append-only.** Once `feed()` returns an event in its `committed`
   list, that event is final for the lifetime of the parser. The consumer's stable scrollback never has to
   retract.
2. **`tentative` is a contiguous suffix of the conceptual event stream.** Concatenating all `committed`
   emitted so far with the most recent `tentative` is exactly what an oracle running on the prefix-of-input
   seen so far would produce.
3. **Full-reparse equivalence.** Feeding the entire input in one `feed()` followed by `finish()` produces a
   committed stream identical to feeding it in N arbitrary chunks followed by `finish()`. The consumer never
   needs a "safety reparse at end" pass. This is a hard guarantee we are committing to.
4. **Source offsets are absolute byte positions** into the full concatenated input, present on every event.
5. **DoS bounds match pulldown-cmark's where they exist** (nested-paren cap 32, link-ref expansion fuel,
   nesting depth ~32). Acceptable to tune later, but we don't go unbounded.
