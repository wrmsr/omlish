# minichain.events — the event bus

The unified event bus a driver scope narrates itself through: every notable thing — user messages, stream deltas,
joined messages, tool executions, timeline mutations, errors — is an `Event` emitted through one `EventsManager` to
an ordered list of callbacks. Frontends, loggers, and the timeline manager are all just subscribers; none of them
know about each other.

## Semantics

- **Synchronous, ordered fan-out.** `emit_event` awaits each registered callback, in registration order, before
  returning. There are no queues between the emitter and subscribers — when an emitting layer's `await` returns,
  every subscriber has fully processed the event. (This is what makes deterministic lock-step testing possible:
  park a stream mid-emission and *everything* prior is settled.)
- **Reentrancy is normal.** A callback may emit (the timeline manager emits `TimelineEvent`s while handling driver
  events); nested dispatch simply runs inline. Guard against self-loops by ignoring your own event types, as the
  timeline manager does.
- **Unknown events are ignored, by convention.** Every subscriber switches on the types it knows and falls through
  silently otherwise. This is load-bearing: it's half of the *streamy-talks-down* contract (see
  `minichain/drivers/README.md` for the full event-ordering contract) — non-stream-aware listeners ignore stream
  events and consume the joined `AiMessagesEvent`; stream-aware listeners must knowingly skip the joined one.
- **Subscribers are good citizens.** A slow callback slows the emitter (and ultimately the driver loop). Decouple
  expensive consumers behind their own buffering (the timeline's subscriptions are the model: synchronous delivery
  into an unbounded per-subscriber queue, drained at the consumer's pace).

## Defining a new event type

Events are frozen dataclasses under the open-polymorphic `Event` base, and **must register their marshal impl** —
events are wire-format by construction (the per-driver JSONL log serializes every one, and remote frontends consume
them marshaled):

```python
@dc.dataclass(frozen=True)
class ThingHappenedEvent(Event, lang.Final):
    thing_id: uuid.UUID

    _: dc.KW_ONLY

    detail: str | None = None


@msh.register_global_lazy_init
def _setup_marshal(cfgs: msh.ConfigRegistry) -> None:
    cfgs.update(Event, *[msh.OpenPolymorphismImpl(et) for et in [
        ThingHappenedEvent,
    ]])
```

Field conventions for the wire/local split:

- Exceptions: `error: BaseException | lang.OpaqueRepr | None` with
  `@msh.update_field_options('error', marshal_via=msh.MarshalVia(lang.OpaqueRepr | None), unmarshal_via=msh.UnmarshalVia(lang.OpaqueRepr | None))`
  — marshals as an opaque repr string, never reconstructed.
- Live-only object references (executors, handles): `@msh.update_field_options('x', no_marshal=True,
  no_unmarshal=True)` and an `| None` type — they simply vanish on the wire.

Every `Event` carries an auto-generated `uuid` from the base.

## Wiring

Per the house injection patterns (see `minichain/INJECT.md`):

- `bind_events()` binds the `EventsManager` and the emit-entry `EventCallback` (so emitting components just take
  `on_event: EventCallback` — they never see the manager).
- Subscribers contribute via the items binder:

  ```python
  mc.injection.event_callbacks().bind_item(
      to_fn=inj.target(o=MyListener)(lambda o: EventCallback(o.handle_event)),
  )
  ```

- A participant that both subscribes *and* emits is a constructor cycle — break it with an `AsyncLate`-resolving
  callback item (the worked example lives in `INJECT.md` and `facades/timelines/inject.py`).
- The bus is **per driver scope**: each driver child injector gets its own manager and callback set. There is no
  process-global bus.
