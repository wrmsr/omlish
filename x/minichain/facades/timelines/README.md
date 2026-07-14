# Timelines

The frontend-agnostic display model of a conversation. A *timeline* is an ordered sequence of *items* - the
domain-shaped things a chat frontend renders (user/ai/thinking messages, unified tool cards, in-flight streaming
items, notices) - maintained live from driver events and/or reconstructed from storage, consumed identically by any
frontend (textual TUI, bare text, web) through windows, watermarked events, and subscriptions.

## The pieces

- **`items`** - the frozen, marshalable item vocabulary. Items have `id` (identity), `revision` (per-item version),
  and `finalized` (will never change again). Where an item corresponds to a message, its id *is* that message's
  `MessageUuid`.
- **`state`** - one timeline's live state: append-ordered items, monotonic *positions*, O(1) id lookup, and the
  monotonic **watermark** bumped by every mutation. Mutations return watermark-stamped events.
- **`events`** - the three-event vocabulary: `Appended` (new item, in full), `Updated` (item changed
  non-incrementally - including *replacement*, where the type changes), `Delta` (item's streaming payload grew by
  `appended`; revision advances by exactly 1). Finalization is item state, not an event kind.
- **`manager`** - the translation pass: an event-bus subscriber folding driver events into state and emitting the
  resulting timeline events back through the bus. See "Reconciliation" below.
- **`translate`** - replay translation: persisted chat slices -> item sequences, pairing tool results into their
  uses' items.
- **`history`** - paged access to the past: windows + opaque realm-tagged cursors, over live state, storage, or (the
  principal impl) the **composite** of both - the persisted prefix stitched to the live suffix, so resume-then-watch
  and scroll-back-while-streaming are one operation.
- **`timeline`** - the facade frontends hold: `attach(limit)` (window + watermark + subscription), `get_latest` /
  `get_before` / `get_after`, subscriptions as async iterables.
- **`projection`** - the client-side state machine: applies an initial window, then events, then backward-paged
  windows, maintaining the ordered id-keyed view a retained UI mirrors. The reference consumer; the coherence tests
  assert `projection(window, events) == state`.
- **`inject`** - `bind_timeline()`: one timeline wired into the enclosing (typically per-driver) scope's event bus.
  Drivers know nothing of timelines; attach the element set or don't, lego-style.

## The contracts

These are load-bearing; code and tests rely on each.

### The watermark contract

Every state mutation increments the timeline's watermark; every emitted event carries it. A snapshot taken at
watermark W plus the events with watermark > W reconstructs live state exactly. Watermarks are strictly increasing,
gapless per timeline.

### The attach recipe

`Timeline.attach` must produce a window and a subscription with *no gap and no overlap* between them, even
mid-stream. Recipe: (1) read the watermark and register the subscription **synchronously - no awaits**; (2) fetch
the initial window, relying on:

### The history coherence invariant

Every `TimelineHistory` implementation must snapshot any *live, mutable* region **synchronously on entry** - before
its first await. Storage reads may then interleave freely with new events: the composite's region filtering (epoch +
live-id dedupe) keeps concurrently-persisted rows out of the window, and buffered events (all > W) apply cleanly on
top.

### The convergence invariant

For every *completed* turn: the item sequence a live watcher ends up with ≡ the item sequence replay translation
reconstructs from storage - same ids, same types, same payloads - **modulo `revision`** (a per-lifecycle fact) **and
live-only fields** (`ToolUseTimelineItem.execution`). Failed turns persist nothing and are live-only. This invariant
is why frontends need exactly one rendering path, not live-vs-replay paths; `tests/test_manager.py::canon_items`
states it operationally, and it has already caught one real driver bug (see `docs/06`).

### Reconciliation (and the event-ordering contract it rides on)

The bus guarantees, per LLM segment: stream deltas (each stamped with a `MessageUuid`) ... then, on success,
`AiMessagesEvent(streamed=True)` carrying the joined canonical messages, *then* that segment's
`ToolUseEvent`/`ToolUseResultEvent`s. The manager exploits this: in-flight items are created at first delta with
`id = MessageUuid`; the joined messages then *replace* them (same id, advanced revision, canonical shape, finalized
where terminal); joined tool messages record call-id -> item-id so execution events advance the same item
(STREAMING -> PENDING -> RUNNING -> COMPLETE). Clean stream end deliberately does **not** finalize - replacement
does; only an exceptional end finalizes in place (with error; STREAMING tool items -> FAILED).

### Windows may overlap; consumers upsert

Window `limit`s are advisory. Storage pages that would open on a tool result extend backward (bounded) until
pairing closes; composite seams dedupe by id but adjacent windows may still share items. Consumers apply window
items by id - `TimelineProjection.prepend_window` is the reference.

### Cursors are opaque

`TimelineCursor`s are resolvable only by (the kind of) history that minted them; `realm`/`key` are implementation
coordinates, not API.

## Wire-format readiness

Items, events, windows, and cursors all marshal (round-trip-stably; tested), with live-only fields explicitly
excluded (`no_marshal`) or wrapped (`OpaqueRepr`). A remote frontend is "attach, serialize the window, stream the
events" - no additional translation layer.

## Testing

Everything here is tested through real wiring - real injector, event bus, ORM (sqlite for multi-session), real tools
- driven by the `scripted` backend (`minichain/backends/scripted`), whose `gate` provides deterministic lock-step
choreography (attach/page/fail at exact mid-stream points; no sleeps). `tests/harness.py` is the entry point;
`tests/test_fizzbuzz.py` is the full offline agent-loop e2e.
