# Ethos

*by Claude Opus 4.8 Max*

*An outsider's reading of this codebase's philosophy, written after a long crawl through `omlish`, `omdev`, and
`ommlds`. This is deliberately a level above `CODESTYLE.md`: not the rules, but the worldview the rules serve. It's
written for a veteran Python programmer, and it dwells on the places where this codebase departs from how Python is
usually written — because those departures are the identity of the thing. Items reference minichain and friends for
examples but are meant to hold everywhere. None of this is authoritative; it's my take, offered as a mirror.
Block-quoted editor's notes are responses from the codebase's author.*


## 1. The codebase is the dependency

The ordinary Python instinct — for any given need, pip-install the community's best-of-breed — is inverted here.
There is an in-house dataclasses system, serde, injector, HTTP client *and* server, SQL layer, ORM, JSON5 parser,
async plumbing, CLI toolkit. External dependencies are exceptional, individually justified, quarantined behind
internal interfaces, optional at runtime wherever possible, and frequently shadowed by internal fallbacks. The short
list of true externalities (`textual`, a few irreproducibles like `greenlet`) is documented like a treaty.

The payoff is visible in the recent git history: timeline pagination needed `ORDER BY`/`LIMIT`/richer `WHERE` support
in the ORM, so *the ORM grew them*, that week, in the same commit stream. When you own the substrate, features are
implemented where they belong rather than worked around where they're permitted. The cost — maintaining everything —
is real, and accepted deliberately: this is infrastructure for a decades-scale personal practice, where control over
evolution compounds and third-party churn is a tax that never stops. Contributions should extend the substrate, not
import around it: if the internal library lacks the thing, the move is to add it, in the substrate's own idiom.


## 2. Values, not objects

Nearly everything that flows between components is a frozen dataclass: identity-free, structurally meaningful,
evolved by `dc.replace`-style `with_` methods rather than mutated. Where ordinary Python objects accrete attributes
across a lifecycle, here data is born complete. Even *history* is value-shaped — messages and content carry their
pre-transform selves as `Original` metadata, so a pipeline's output remembers what it was computed from.

Mutability is not banned; it's *housed*. State lives in explicitly stateful classes — managers, sessions,
accumulators — whose mutable fields are single-underscore-private and whose accessors are typed immutably
(`Sequence`, `Mapping`, `AbstractSet`) or return defensive copies. The boundary between value-world and state-world
is the most carefully patrolled border in the codebase, and most design errors here are border violations: a value
that secretly aliases, a manager that leaks its internals.


## 3. Types are made to carry meaning

This codebase mints types the way ordinary Python mints string keys. Scalar wrappers (`ChatId`, `DriverId`,
`ApiKey`), `NewType`s over sequences, and above all `tv.TypedValues` — heterogeneous collections *keyed by type*,
used in place of `**kwargs` and giant config objects. An option isn't `temperature=0.7`; it's `Temperature(0.7)`, an
instance of a type whose position in a small, documented family determines which services may accept it. The
`services` README reasons about request/response *variance* the way a library elsewhere might reason about REST
verbs — the type relationships are the API contract, and `static_check_is_*` decorators assert conformance purely at
type-check time, with negative tests enforced via `warn_unused_ignores`.

Notably, this is **nominal**, not structural, typing by preference — a deliberate counter to the Protocol-everywhere
fashion. "It is desirable that not all functions returning an `int` are `UserIdProvider`s." Protocols appear rarely
and only where reflection or variance genuinely demands them (the single-method `Service` being the canonical,
heavily documented exception). For a contributor the instinct to internalize: when two things of the same Python type
mean different things, *make them different types*; when behavior varies, key it on a type, not a string.


## 4. Closed worlds: class hierarchies as ADTs

Python culture prizes openness — duck typing, monkey-patchable everything, subclass-me-anywhere. This codebase
builds *algebraic data types* out of classes and means it: `lang.Abstract`, `lang.Sealed`, `lang.PackageSealed`,
`lang.Final` mark hierarchies as closed sums, consumed by exhaustive `isinstance` dispatch with a trailing
`raise TypeError`. Some bases go further and enforce their naming conventions in `__init_subclass__`
(`check.state(cls.__name__.endswith('RequestMetadata'))`) — the family's grammar is checked at class-definition
time, not in review.

Two related departures: `abc.ABC` is banned in favor of `lang.Abstract` (subclass-definition-time enforcement, and
`ABCMeta`'s 6x `isinstance` overhead is unacceptable in code that dispatches on types this much); and for marking
subgroups within a closed family, an empty abstract mixin is usually preferred over a `Union` alias — the marker
participates in `isinstance`, the alias doesn't. The reader should treat an unsealed, unmarked class hierarchy as a
smell: either it's meant to be open (rare, deliberate) or someone forgot to say what it is.


## 5. Compiler discipline over runtime data

The signature *shape* of this codebase is the IR-and-passes pipeline. Chat messages and content form small typed
trees; around them stand families of transforms (`MessageTransform`, `ContentTransform`, delta transforms),
renderers, visitors, parsers, and joiners — each tiny, stateless where possible, composable (`Composite*`,
`TypeFiltered*`, `Fn*`). Backend integrations are converging on the same shape: a vendor 'protocol' IR plus
translation passes in and out, rather than ad-hoc dict-wrangling at call sites. Even streaming is pass-shaped — a
delta stream is transformed (uuid-stamping), tee'd (event emission), and folded (joining) like a token stream
through compiler stages.

The deeper habit: when behavior over data gets complicated, the move is not a smarter object with more methods, but
a *new pass* over dumb data — and when a pass needs memory, it becomes a small stateful class with one `transform`
method, not a framework. This keeps the data model the stable center while behaviors multiply at the edges, which
is precisely what lets one IR serve N backends and M frontends.


## 6. Wiring is a place, not a property

The codebase is written *for* a guice-style dependency injector while remaining fully usable without one — and the
discipline that squares that circle is locational: all actual wiring lives in `inject.py` modules (binders; the
moral equivalent of guice modules), all wiring *helpers* in `injection.py`, and nothing anywhere else may import the
injector. Classes are injector-shaped — dependencies as constructor kwargs, sensible defaults, fine-grained
decomposition — but injector-ignorant. Applications, in turn, are mostly *declarative*: a `main()` here is a few
lines that compose binder elements from config dataclasses and ask the injector for one root object; behavior
differences (streaming vs not, tools on or off, which frontend) are expressed as different bindings, including
wrapper *stacks* composed bottom-to-top (`wrapper_binder_helper`) and per-instance scopes via child injectors (one
per chat driver).

For a Python veteran this is the most foreign tenet — DI containers are usually mocked here as Java cosplay — and
the counter-argument is in the testing tenet below: the injector is what makes mock-free testing ergonomic, because
substituting a real-but-simple implementation is an `inj.override` away. The norm to absorb: adding a feature means
adding a class *and its binding*; reading a feature means starting from its `inject.py` to see the composition
before reading any implementation.

> ***[editor's note — from the codebase's author]*** All true, with one re-weighting: in the 'real' code this
> aspires to be, the testing capability is a *major* point of this arrangement, but not the *main* one. The main one
> is the toolbox-full-of-legos quality: composable strategies, layers, and mix-and-match capabilities, all
> configurable and safely wireable together while themselves remaining more or less ignorant of one another. And —
> in a bit of a philosophical departure from guice, being a team of one dev rather than tens of thousands — there's
> a deliberate enticement toward a degree of *dynamic* configuration in the binders/modules themselves; certainly
> much more so than hardcoding these kinds of compositions in constructors selected by some
> `strategy: ta.Literal[...]` kwarg. (The feasibility of which is further boosted by the marshal system *also* being
> in-house, and thus able to be made to deserialize whatever configgy-object-thingies the binders want to be driven
> by.)


## 7. Laziness is infrastructure

`import omlish.lang` is engineered to be near-free; `import minichain as mc` exposes a thousand names and imports
instantly. This is achieved by treating the import graph as a managed artifact: `auto_proxy_init` facades that
late-load submodules on attribute access, `proxy_import` for heavy modules, manifests (`.omlish-manifests.json`)
that let packages advertise metadata *without being imported*, and ahead-of-time generated `_dataclasses.py` files
that exist purely to make dataclass-heavy packages import fast. The rule that heavy imports must be whole-module
(`import torch`, never `from torch import Tensor`) exists *because* the laziness machinery operates at module
granularity.

> ***[editor's note — from the codebase's author]*** The whole-module rule is actually *both* for style *and* for
> the lazy machinery. The style preference came first, and grew out of watching annotation laziness set in (the
> author's own included): rather than adding the thirtieth `from typing import ...` to get the type form one
> actually needs — the most restrictive one that fits, like a proper immutable `AbstractSet` — the temptation is to
> just slap a looser, mutable annotation on it and hope readers know not to mutate. With everything 'on tap' as
> `ta.`, the right annotation is always one attribute away — and then it simply wound up being overall nicer, and
> more uniform, to have everything on tap everywhere.

The consequence for contributors: the `__init__.py` facade of a package is its public map and is curated by hand —
adding something real means adding it there too — and module-body work is forbidden (no IO, no loops, no eager
anything) not as nagging but because module bodies execute at unpredictable times by design.


## 8. No mocks. Build the real small thing.

The testing stance is the most counter-cultural item here. Patching is effectively banned; `Mock` objects don't
appear; the unit-test-per-method reflex is explicitly unwanted. The desired economy is thick end-to-end tests
through the real wiring — real injector, real event bus, real ORM (in-memory store), real driver loop — at roughly
a 4:1 impl-to-test ratio, with small unit tests reserved for genuinely isolated algorithmic bits. Where a test needs
to control a dependency, the answer is a *real but simple implementation* of the interface (the dict-backed user
service instead of the remote one), which usually turns out to be useful production code anyway — the codestyle even
declines the word 'fake' for these.

Concurrency testing follows the same realism: no sleeps, ever; lock-step schedules at explicit synchronization
points; an aspiration to reproduce every realistic failure at each IO boundary. The honest caveat (true at the time
of writing, in minichain at least): where a good simple implementation is *missing* — e.g. a programmable chat
backend — the e2e ideal silently degrades into either online-only tests or the unittesty drift this philosophy
abhors. The simple implementations are therefore not test conveniences; they are *load-bearing philosophy*, and
building one is some of the highest-value work in the repo.


## 9. Uniformity is a feature; navigation is by convention

Every module looks like every module: the `##` divider after imports, one-import-per-line, stdlib as whole modules,
TypeVars above the fold, `_main()` at the bottom, callee-before-caller flow, nouns for modules and verbs for
functions, small files in deep packages. None of these rules is individually load-bearing; their *uniformity* is.
You navigate this codebase by pattern-matching, not by search: any `inject.py` reads like every other, so the
fifteenth one costs nothing; you know where the public surface is (`__init__.py`), where the wiring is, where the
types live, without looking. It's the same bet monorepos at large companies make, scaled to one author — and it is
exactly what makes the codebase *more* tractable for code agents than its size suggests, since agents are
pattern-matchers above all.

The corollary discipline: innovations in *structure* should be resisted even when locally appealing. A contribution
that's stylistically novel is wrong even if it's good, because it spends the uniformity budget. (Mechanical
enforcement exists — ruff/flake8/mypy via `make check` — but the real enforcement is that deviation is conspicuous.)


## 10. Magic is permitted where it's load-bearing — and fenced

This is not an anti-magic codebase. There's a full runtime reflection system over typing constructs, dataclass
machinery that rivals attrs in ambition, generated code, dynamic dunder installation, a coroutine trampoline that
manually drives `send`/`throw` to invert a sink into an iterator, and contextvar-carried implicit parameters
(`contextual`). What distinguishes it from cleverness-soup is that each piece of magic is (a) in service of a stated
structural goal — laziness, immutability, type-forwardness — (b) wrapped in a small named utility with a boring
interface, and (c) *contained*: callers of `new_stream_response` never see the trampoline; users of `lang.cached`
never see the descriptor protocol.

The norm: magic may be built, but not *ambient*. If a trick leaks into call sites — if ordinary code has to know
about the metaclass, the proxy, the frame-hack — it's wrong. And plain code is still the default: the magic exists
so that the other 95% of the codebase can be extremely boring frozen dataclasses and explicit functions.


## 11. Everything is already wire-format

Serialization is a design input, not an afterthought. Domain types — messages, events, content nodes, options —
register their marshal behavior *adjacent to their definition* (polymorphism sets, field options, lazy global
registrations), so the question "can this cross a process boundary?" is answered *yes, by construction* years before
any process boundary exists. Live-only fields (an executor handle, an exception) are explicitly marked unmarshalable
or wrapped in `OpaqueRepr`, making the wire/local split legible in the type itself. Events JSONL-log themselves as
an audit trail as a side effect of existing.

This is the quiet enabler of the codebase's stated future (remote sessions, web frontends, attachable clients): the
hard part of distribution — agreeing on what the data *is* — is amortized into every type definition. The
contributor norm is to keep paying that tax: a new event or item type isn't done until its marshal story (including
what it does *not* serialize) is declared.


## 12. Deployment shapes the dialect

A substantial subset of the codebase is written in a second dialect — 'lite' code: Python 3.8-compatible, zero
dependencies, stdlib annotations, written so an amalgamator can stitch whole subsystems into a single
self-contained `.py` file that ships by being scp'd. The dialect's oddities (single-line type aliases, no name
mangling, namespace-bag classes standing in for modules) all derive from that deployment story. Standard code makes
the complementary bet: 3.14-only, free to use the newest language features immediately.

The general principle is that *how code will run is a first-class design constraint*: no `__file__` (zipapp/oxidized
dists are assumed), resources via package-resource APIs, no environment variable configuration (injected config
only), forkable process supervisors get selector-based IO rather than asyncio because asyncio spawns threads. Where
most Python projects discover their deployment constraints late and retrofit, here the runtime envelope is part of
each module's identity from the first line (`# @om-lite`).


## 13. The monorepo is a refinery, not a museum

Code here has a *lifecycle gradient*: experiments and curiosities in `x/`, core-adjacent but unsettled code in
`omxtra` ("usually in the process of either moving out of or moving into `omlish` proper, or being demoted"),
production substrate in `omlish`, with `omdev`/`ommlds`/`ominfra` as domain rings. Graduation and demotion are
normal, expected motions — nothing is precious about where it currently sits, and the author routinely rewrites,
renames, and relocates wholesale (the git history is full of "Refactor X layout" commits that would be politically
impossible in a team repo).

Two implications. First, *location is information*: code's ring tells you its stability contract, and depending
inward is free while depending outward is forbidden (clean-architecture dependency direction, enforced by
convention). Second, foundations are built **by shaping, not by featuring** — the YAGNI objection is answered not
by building speculative features but by keeping the *shape* of things (immutable, typed, marshalable, decoupled)
ready for stated future directions: forkable chats, attachable remote sessions, multiple frontends. Speculation
lives in the bones, not in dead code.


## 14. Async without forking the world

The codebase refuses, where it can, to maintain parallel sync and async universes. `SyncAsync` adapters wrap clients;
sync DBs are lifted into async via dedicated executors; the async backend itself is abstracted (anyio-preferred, asyncio
where hosts demand it — textual — with an in-house pytest plugin so all backends test through one fixture). And async
code is written with unusual care at the *cancellation* seams: `shielded_finally` for must-run finalizers, explicit
state machines on stream lifecycles, a `BaseException`-derived cancellation sentinel threaded through the stream
trampoline. 'Everything that does IO needs a timeout' is policy, with defaults sized to intent (minutes interactive, an
hour background).

The contributor instinct to unlearn: writing `foo()` and `afoo()` twins, or assuming asyncio. Write to the
abstraction; let adapters and the injector pick the color and the loop.


## Coda: what this asks of a contribution

Read the neighboring file before writing yours; the codebase teaches by example and expects to be learned that way.
When meaning varies, mint a type. When behavior varies, write a pass or an implementation, and bind it in the
`inject.py` where it belongs. Keep values frozen and state housed. Make the new thing marshal, make it lazy, make it
look like everything else. Test it through its real wiring, end to end, with a simple real implementation where the
world would intrude — and if that simple implementation doesn't exist yet, recognize that building it *is* the work.
Leave the substrate stronger than you found it: the point of this place is not any one feature, but that the next
feature is always slightly easier than the last.
