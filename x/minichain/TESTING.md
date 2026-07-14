# Testing minichain (and its frontends)

How tests are written here, and — more importantly — how the offline end-to-end machinery works, because the house
testing philosophy is unreachable without it. `CODESTYLE.md`'s Tests section states the rules; this document is the
practice.

The philosophy in one paragraph: **thick, real, end-to-end integration tests, through the real wiring** — real
injector, real event bus, real ORM, real tool execution — at roughly a 4:1 impl-to-test weighting, with small unit
tests reserved for genuinely isolated algorithmic pieces. **No mocks. No patching. Ever.** Where a test must control
a dependency, the answer is a *real but simple implementation* of its interface, substituted via `inj.override` —
and those implementations are production code, not test scaffolding (they tend to become genuinely useful: the
`scripted` backend doubles as the offline demo backend). **No sleeps** — tests synchronize explicitly and complete
deterministically.

History note, so the lesson isn't relearned: before the scripted backend existed, the only chat-stack tests an
offline contributor *could* run were isolated state tests — and that's exactly the code shape that got produced.
The capability defines the style. If you find yourself writing fine-grained unit tests against hand-synthesized
inputs, first ask whether the real loop can produce those inputs for you.


## The offline stack, bottom to top

### The scripted backend (`minichain/backends/scripted`)

A fully programmable chat backend: a `ChatScript` is a sequence of turns, one consumed per LLM invocation; each turn
is most easily built from messages, from which realistic wire-shaped delta streams are derived (chunked content,
partial-tool-use args, thinking):

```python
script = mc.ChatScript([
    mc.ChatScriptTurn.of(
        mc.AiMessage('Let me check.'),
        mc.ToolUseMessage(mc.ToolUse(id='call_1', name='weather', args={'location': 'Tokyo'})),
    ),
    mc.ChatScriptTurn.of(
        mc.AiMessage('Foggy, naturally.'),
        expect=lambda chat: ...,   # assert on the incoming request - fail at the turn that went wrong
    ),
])
```

- `expect` hooks make multi-turn tests fail *where* the conversation derailed, not at the end.
- `chunk_size` controls delta granularity (one delta per emission); `indexed_tool_uses=True` produces the
  parallel-call wire form.
- Exhaustion policies: `'raise'` (tests), `'repeat_last'`, `'restart'` (the demo loop).
- The non-stream service consumes the same turns *joined through the real `AiDeltaJoiner`* — using it continuously
  re-proves joiner fidelity.

**Statefulness caveat**: service-provider machinery (the registry/`-b scripted` path) instantiates a fresh backend
per invocation, resetting the turn cursor. When a script must survive that path, pass a **shared cursor** instead of
a bare script: `mc.ScriptedChatCursor(mc.ChatScriptCursor(script))` (e.g. via `BackendConfig.configs` in the cli).
Direct-instance wiring (below) doesn't have this problem.

### The gate: deterministic mid-stream choreography

`ChatScript(gate=...)` names an async hook called before every emission (and once after the last, stream still
open). `PausingGate` (in the timelines test harness) turns it into a lock-step lever:

```python
gate = PausingGate(lambda pt: pt.invocation_index == 0 and pt.emission_index == 4)
script = mc.ChatScript([...], gate=gate)

task = asyncio.create_task(h.send_user_text('hi'))
await gate.wait_paused()      # the stream is parked; every prior emission fully processed by ALL bus callbacks
...attach / snapshot / page / assert mid-stream things...
gate.resume()
await task
```

When `wait_paused()` returns, the world is frozen at an exact, repeatable point. This is how attach-coherence,
scrollback-while-streaming, and mid-stream failure are tested without a single sleep. For failure injection, a gate
that raises *is* the fault:

```python
async def gate(pt):
    if pt.emission_index == 3:
        raise RuntimeError('scripted mid-stream failure')
```

### Driver wiring (`minichain/drivers/testing.py`)

`bind_scripted_driver(script, cfg, *, chat_id=..., db_file_path=...)` is the complete real driver over the scripted
backend (stream or not per `cfg.ai.stream`), with allow-all tool permissions. The basic shape:

```python
async with inj.create_async_managed_injector(
    bind_scripted_driver(script, DriverConfig(ai=AiConfig(stream=True, enable_tools=True))),
    bind_weather_test(),                                # a real module contributing a real tool
    event_callbacks().bind_item(to_const=on_event),     # record the bus if you want it
) as injector:
    driver = await injector[Driver]
    await driver.start()
    await driver.do_action(SendUserMessagesAction([user_message('hi')]))
    ...
```

**Storage**: the default in-memory store cannot be shared across injectors (its tables key on mapper identity) —
for multi-session/resume scenarios pass `db_file_path=str(tmp_path / 'state.db')` and run *real sqlite*, which is
better anyway (real schema create, real resume, and it's what shook out real concurrency bugs).

### The timelines harness (`minichain/facades/timelines/tests/harness.py`)

`timeline_driver_harness(script, ...)` is the one-stop async context manager: scripted driver + a bound `Timeline` +
an event recorder, yielding direct handles (`driver`, `storage`, `manager`, `timeline`, `events`, `injector`) and
`send_user_text`. Most timeline-area tests are a script, a harness, and assertions.


## Invariants as test spines

Prefer asserting *properties* over enumerating cases — properties catch the bugs nobody enumerated:

- **Convergence**: for every completed turn, live state ≡ replay translation of storage, modulo `revision` and
  live-only fields. Operationally: `canon_items(live) == canon_items(translate_chat(await storage.get_chat()))`.
  This single line, run after any scenario, has caught real cross-layer bugs (e.g. emitted-vs-persisted metadata
  divergence).
- **Attach coherence**: `projection(window@W) + events>W == state` — *exactly*, object-equal, regardless of when
  the attach happened. Park mid-anything with a gate and assert it.

When you add a scenario, run it *through the invariants* before writing scenario-specific assertions.


## Frontend testing

**Textual** — the real `ChatApp` runs headless under textual's pilot, through the real injector chain and registry
backend resolution:

```python
async with inj.create_async_managed_injector(inj.override(
    bind_main(entrypoint_cfg=chat_cfg),
    inj.bind(tx.DevtoolsSetup, to_const=tx.DevtoolsSetup(lambda app: None)),     # headless: no devtools
    inj.bind(BackgroundTerminalRenderer, to_ctor=_NopBackgroundTerminalRenderer, singleton=True),
)) as injector:
    app = await injector[ChatApp]
    async with app.run_test() as pilot:
        ...
```

- The no-op overrides are real-but-simpler implementations, per the philosophy — scrollback writes and devtools
  connections are meaningless headless.
- **Never poll with sleeps**; pump: `for _ in range(n): (return if cond) ; await pilot.pause()`. Combine with a
  gate to make mid-stream widget states *deterministic* rather than raced.
- pytest-timeout's signal kill truncates diagnostics on hangs — when debugging a pump that exhausts, temporarily
  dump app/widget state at the exhaustion point rather than re-running blind.

**Bare/cli** — go through the *actual* arg path: `_run_entrypoint_cfg(ChatProfile().configure(['-bscripted', '-n',
'--db', db, 'hi']))` with `capsys` for output. **Web** — drive the ASGI callables directly (hand-rolled
receive/send), no server needed; assert by unmarshaling the wire bytes back into a `TimelineProjection`.


## Conventions

- `@pytest.mark.asyncs('asyncio')` (the in-house plugin), not `pytest.mark.asyncio`.
- Don't type-annotate test functions; raw `assert`s liberally; `pytest.raises` for errors; `tmp_path` over manual
  tempdirs; instantiate data inline rather than via fixtures.
- Tests live in `tests/` subpackages (with `__init__.py`); cross-package *test* imports of shared harnesses are
  acceptable (imports still point inward).
- Run targeted: `./python -m pytest ommlds/minichain/facades/timelines/ -q`. Before committing: `make fix gen
  check` plus the relevant suites.

## What not to do

`unittest.mock` / `patch` in any form; `time.sleep`/`asyncio.sleep` as synchronization; hand-synthesized event
sequences when a scripted driver run produces real ones; one test file per source file out of symmetry. If a thing
seems untestable without a mock, the missing piece is a simple real implementation — building it is in-scope work,
and historically the highest-leverage kind.
