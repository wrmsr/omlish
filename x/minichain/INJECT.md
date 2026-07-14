# Injection in minichain (and friends)

**Read [`omcore/inject/README.md`](../../omcore/inject/README.md) first.** It covers the injector itself — keys,
bindings, providers, elements, injectors, scopes. This document covers everything *between* that API and writing
internally-idiomatic wiring in this codebase: the conventions, the recurring composition patterns, and the sharp
edges. minichain is currently the injector's heaviest user, but nothing here is minichain-specific — these are the
house patterns wherever the injector appears.

The mindset shift for a Python veteran: applications here are mostly *declarative*. A `main()` is a few lines that
compose binder elements from config dataclasses and ask the injector for one root object. Behavior differences —
streaming vs not, which frontend, tools on or off — are expressed as *different bindings*, not branches in logic.
The payoff is a toolbox of composable, mutually-ignorant parts ("legos"), with mock-free testing via substitution
falling out for free.


## The quarantine convention

The injector lives in exactly two kinds of module, and **nowhere else**:

- **`inject.py`** — *binder* modules: functions returning `inj.Elements`, the moral equivalent of Guice modules.
  This is where actual wiring lives.
- **`injection.py`** — wiring *helpers*: reusable, package-related binding utilities (items-binder helpers,
  injector-aware adapter classes) — but not actual wiring.

Everything else is written *for* the injector but remains injector-*ignorant*: dependencies as keyword-only
constructor arguments, sensible defaults where possible, no service-locator reaching, no injector imports. The point
is that all of it must remain fully usable without the injector — construct things by hand in tests or scripts and
they work.

A package's binder typically composes its children's binders, mirroring the package tree:

```python
def bind_driver(cfg: DriverConfig = DriverConfig()) -> inj.Elements:
    els: list[inj.Elemental] = []

    els.extend([
        bind_ai(cfg.ai),
        bind_storage(cfg.storage),
        bind_tools(cfg.tools),
    ])

    ...

    return inj.as_elements(*els)
```


## Anatomy of a binder module

```python
from omcore import inject as inj
from omcore import lang

from .configs import FooConfig


with lang.auto_proxy_import(globals()):
    from . import impl as _impl
    from . import types as _types


##


def bind_foo(cfg: FooConfig = FooConfig()) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.extend([
        inj.bind(_impl.FooImpl, singleton=True),
        inj.bind(_types.Foo, to_key=_impl.FooImpl),
    ])

    #

    if cfg.enable_bar:
        els.append(inj.bind(_impl.BarThing, singleton=True))

    #

    return inj.as_elements(*els)
```

Things to notice, all deliberate:

- **The `auto_proxy_import` header.** Binders are imported eagerly (by parent binders, by `main()`s) but the guts
  they wire should load only when actually provided. Proxied names work fine in type annotations (3.14 deferred
  annotations) and inside binding closures. Configs are imported eagerly — they're cheap dataclasses and binder
  *signatures* need them.
- **Config in, elements out.** Binders take a frozen config dataclass (defaulted) and branch on it. Config objects
  are how dynamism enters wiring — and since the marshal system is in-house, configs can ultimately come from
  files/args/wherever.
- **`els: list[inj.Elemental]` accumulated in `#`-separated stanzas**, one concern per stanza.
- **`singleton=True` is explicit.** Unscoped is the default; say singleton when you mean it (you usually do for
  service-ish objects).
- **Interface/impl pairs** bind the impl, then *link* the interface to it (`to_key=`). Consumers depend on the
  interface key; tests and alternate frontends rebind it.


## The provider-function pattern

Binding a class directly (`inj.bind(FooImpl, singleton=True)`) constructor-injects **every annotated parameter** —
including optional ones, which it will try to resolve. If the injector cannot resolve a param with a default, that is
not an injection failure - the param will not be included in the instantiation kwargs, and thus the default will take
effect. When a constructor has params the injector shouldn't touch (tuning knobs, `| None = None` extras), bind a
provider function instead; its *return annotation* is the key:

```python
def _provide_timeline_manager(events: EventsManager) -> TimelineManager:
    return TimelineManager(events=events)  # other ctor params left to their defaults

els.append(inj.bind(_provide_timeline_manager, singleton=True))
```

For one-liners there's `inj.target`, which names the dependencies and wraps a callable:

```python
els.append(inj.bind(
    EventCallback,
    to_fn=inj.target(em=EventsManager)(lambda em: EventCallback(em.emit_event)),
    singleton=True,
))
```

A captured dependency is resolved **when the binding is provided**, not lazily on use — if you need lazy, see
"Late bindings" below.


## Plugin collections: the items-binder helper

The standard way for packages to *contribute* into an extensible collection (event callbacks, tool catalog entries,
backend configs, item presenters...). Three pieces:

**1.** A `NewType`'d sequence as the collection's key, and a cached helper in `injection.py`:

```python
# types.py
FooHandlers = ta.NewType('FooHandlers', ta.Sequence[FooHandler])

# injection.py
@lang.cached_function
def foo_handlers() -> inj.ItemsBinderHelper[FooHandler]:
    return inj.items_binder_helper[FooHandler](FooHandlers)
```

**2.** The owning package's binder binds the *provider* (the collector):

```python
els.append(foo_handlers().bind_items_provider(singleton=True))
```

**3.** Any other package's binder contributes items:

```python
els.append(foo_handlers().bind_item_consts(MyFooHandler()))           # constants

els.append(foo_handlers().bind_item(to_ctor=MyFooHandler, singleton=True))  # injected

els.append(foo_handlers().bind_item(                                  # adapted
    to_fn=inj.target(o=SomeService)(lambda o: FooHandler(o.handle)),
))
```

Consumers just take `handlers: FooHandlers` in their constructors. Order is registration order; an empty collection
is fine.

**The big caveat: items do not cross child-injector boundaries.** The provider collects only items bound in *its
own* injector's elements. An item bound in a parent is invisible to a child's provider (and vice versa). If a value
needs to become an item inside a child scope, carry it there *as data on a config object* and have the child-scope
binder contribute it:

```python
@dc.dataclass(frozen=True, kw_only=True)
class BackendConfig:
    configs: ta.Sequence[mc.Config] | None = None

# ...in the binder that runs inside the child scope:
if (bcs := cfg.backend.configs):
    els.append(backend_configs().bind_item_consts(*bcs))
```


## Wrapper stacks

For decorator-composed implementations (the most load-bearing pattern in the driver), build the stack in the
binder, bottom-to-top, and bind the interface to the top:

```python
stack = inj.wrapper_binder_helper(AiChatGenerator)

els.append(stack.push_bind(to_ctor=ServiceAiChatGenerator, singleton=True))
els.append(stack.push_bind(to_ctor=TransformingAiChatGenerator, singleton=True))
els.append(stack.push_bind(to_ctor=EventEmittingAiChatGenerator, singleton=True))

if cfg.enable_tools:
    els.append(stack.push_bind(to_ctor=ToolExecutingAiChatGenerator, singleton=True))

els.append(inj.bind(AiChatGenerator, to_key=stack.top))
```

Each pushed class takes an `AiChatGenerator` (the layer below) as a constructor kwarg. Composition lives *here*,
declaratively — not in constructors behind a `strategy: ta.Literal[...]` kwarg. Order matters and is *semantic* (e.g.
event emitters sit outside metadata stampers so emitted values are the canonical ones); when you reorder a stack, say
why in a comment.

`push_bind(..., with_=[...])` rebinds keys for that layer's construction only — e.g. handing a wrapper a specific
inner key under the public interface name.


## Overrides

`inj.override(elements, *overriding)` re-binds matching keys within an element set — duplicate keys are otherwise a
hard `ConflictingKeyError` (there is deliberately no silent last-wins). Two canonical uses:

```python
# A frontend specializing library defaults:
els.append(inj.override(
    mc.facades.inject.bind_facade(cfg.facade),

    inj.bind(_provide_my_quit_handler, singleton=True),
))

# A test substituting a real-but-simple implementation (never a mock):
async with inj.create_async_managed_injector(
    inj.override(
        bind_driver(cfg),

        inj.bind(ToolPermissionDecider, to_key=AllowAllToolPermissionDecider),
    ),
) as injector:
    ...
```


## Late bindings, getters, and breaking cycles

`inj.bind_async_late(Foo)` binds `inj.AsyncLate[Foo]` — a callable that resolves `Foo` from the injector on first
call. With a second argument it populates a *named getter* class instead, which keeps inject machinery out of
domain signatures:

```python
class DriverGetter(lang.Func0[ta.Awaitable['Driver']]):
    pass

els.append(inj.bind_async_late(Driver, DriverGetter))

# ...elsewhere, a domain class takes the getter:
def __init__(self, *, driver: DriverGetter) -> None: ...
```

The canonical cycle this breaks: **a bus participant that both subscribes and emits**. The events manager needs the
callbacks collection; a callback that needs the events manager (to emit) is a cycle. Resolve the participant lazily
at the *callback* level, keeping its own constructor clean:

```python
def _provide_manager_callback(late_m: inj.AsyncLate[TimelineManager]) -> EventCallback:
    async def inner(event: Event) -> None:
        await (await late_m()).handle_event(event)

    return EventCallback(inner)

els.extend([
    inj.bind(_provide_timeline_manager, singleton=True),
    inj.bind_async_late(TimelineManager),
    event_callbacks().bind_item(to_fn=_provide_manager_callback, singleton=True),
])
```

(`AsyncLate` references stay inside `inject.py`, per its own docstring's warning — domain code gets named getters
or nothing.)


## Child injectors as scopes

Rather than custom scope machinery, per-instance scoping is usually a *child injector*: collect a fresh element set
(rebinding per-instance identities), create it with `parent=`, and manage its lifetime with an exit stack:

```python
aes = contextlib.AsyncExitStack()
await aes.__aenter__()

ec = inj.collect_elements(inj.as_elements(
    inj.bind(contextlib.AsyncExitStack, to_const=aes),

    bind_one_driver(cfg),   # binds DriverId, ChatId, the event bus, the timeline, ...
))

child = await inj.create_async_injector(ec, parent=parent_injector)
```

Unbound keys fall through to the parent; keys bound in the child shadow it. This is how "N chat drivers in one app"
works: each driver gets its own bus, storage manager, and timeline, while sharing app-level singletons. Remember the
items caveat above — contributions don't flow across the boundary; configs do.

Managed lifecycles: `inj.create_async_managed_injector(...)` is the usual entrypoint (an async context manager);
`inj.make_async_managed_provider(Cls, ...)` binds a context-managed instance whose `__aexit__` runs at injector
close, and binding an `AsyncExitStack` const gives provider functions something to register cleanup on.


## Sharp edges checklist

- **Class binding injects every annotated ctor param.** Defaulted params are not skipped. Provider functions are
  the escape hatch.
- **Duplicate keys are errors.** Compose with `inj.override`, don't rebind and hope.
- **Items don't cross parent/child injectors.** Thread data via configs into the child's binder.
- **`inj.target` captures resolve at provide time** of that binding, not lazily — use `AsyncLate`/getters for lazy.
- **Eagerness propagates.** A provider that builds adapter objects from resolved keys (e.g. context providers)
  instantiates those dependencies when *it* is provided, even if they're never used — if construction is expensive
  or demands further bindings, tests must bind or override them.
- **NewTypes are real keys.** `ta.NewType('ServerPort', int)` keeps an `int` injectable without ambiguity; tags
  (`inj.as_key(Conn, tag='primary')`) handle same-type multiples.
- **Singleton is opt-in**, per binding. Forgetting it on a stateful service means N instances and very confusing
  bugs.
- **Annotations referencing proxied imports are fine**; *evaluating* them at module import time (e.g. a module-level
  alias) defeats the laziness.

When in doubt, pattern-match a neighboring `inject.py` — they are deliberately uniform, and the uniformity is the
documentation of record between this file's revisions.
