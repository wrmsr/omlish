# minichain.ui — UiText (and the two-IRs doctrine)

This package holds **UiText**, the user-facing display IR. Understanding it starts with a doctrine that isn't
visible from any single module:

## Content is for models; UiText is for humans

minichain has *two* display-ish IRs, on purpose, with **deliberately disjoint capabilities**:

- **`Content`** (`minichain/content/`) is the currency of the *model* conversation — what LLMs ingest and produce.
  It has parse/render/transform passes, markdown-ish structure, images, placeholders. Anything that is part of a
  message, a tool result, or a prompt is Content, because a model may read it.
- **`UiText`** (this package) is sent to the (probably human) *user* and is **never seen by a model**. It has
  things models don't ingest — colors, styling, diffs, someday spinners with frontend animation state — and lacks
  things terminals can't show. Notices, status, tool-card chrome, presenter output (e.g. an edit shown as a diff):
  UiText.

When deciding where something goes, ask *who reads it*. A tool's **result** is Content (the model reasons over it);
how that result is **displayed** may be UiText (via timeline item presenters — see
`facades/timelines/presenting.py`). The two never convert implicitly.

## UiText in practice

A small sealed node family — `StrUiText`, `ConcatUiText`, `StyleUiText`, `JsonUiText`, `DiffUiText` — with
aggressive normalization through the `UiText.of(...)` constructor (strings merge, nests flatten, blanks drop):

```python
from ommlds import minichain as mc

t = mc.UiText.of([
    'tool ',
    mc.UiText.of('weather').style(bold=True),
    ' ',
    mc.UiText.of('running').style(color='yellow', italic=True),
])

s = str(t)                      # plain text, styles dropped
rt = mc.ui_text_to_rich_text(t) # rich Text with nested style inheritance, for textual frontends
```

`CanUiText` (`UiText | str | sequences thereof`) is the accepted input type everywhere; normalize at boundaries
with `UiText.of` / `UiText.str_of`. `join` and `style` are the combinators. Styles are deliberately minimal
(a small color literal set, bold, italic) — grow them with restraint; every frontend must be able to degrade them.

### Diffs

`DiffUiText` carries an old→new change *as data* (`old`, `new`, optional `path`); the unified-diff rendering is
derived — plain text via `str()`, colorized (+green/−red/@@cyan) through the rich adapter:

```python
d = mc.DiffUiText(old=old_text, new=new_text, path='fizzbuzz.py')
```

This is the canonical "show an edit" shape — produced e.g. by the fs module's `edit_file` timeline presenter.

### Json

`JsonUiText(v)` defers compact json rendering of a value; `render_obj_json_ui_text(...)` (in `ui/json.py`) builds
richer pretty/json5 renderings as Str/Style trees.

## Properties to preserve when extending

- **Marshalable.** All nodes round-trip through the marshal system (UiText flows over the wire in timeline items
  and events). A new node type must marshal, and what it carries should be *data*, with rendering derived — like
  `DiffUiText`, not a pre-rendered escape-code string.
- **Plain-text always works.** `write_str_to`/`__str__` must produce a sensible degraded rendering; styling is
  enhancement, never load-bearing meaning.
- **Frontends opt in per node.** The rich adapter (`ui/rich.py`) raises `TypeError` on nodes it doesn't know —
  extend every adapter when adding a node, or document the omission.
- **Sealed and normalized.** New nodes join the sealed family here, and `UiText.of` should know how (or whether) to
  normalize them.
