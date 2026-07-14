# Caching And Threads

This checkpoint records the current caching discussion, the concrete runtime use cases driving it, the provisional cache
state in the code, and the thread-safety questions that need to stay visible as the reflection system matures.

## Context

`mypydistill` is intended to replace the old runtime reflection system for real `omcore` use cases. That replacement is
not only about correctness or richer type semantics. It also has to preserve the old system's practical performance
shape.

The hot entry point in the old world is effectively:

```python
rfl.typeof(obj)
```

The new equivalent is currently:

```python
RuntimeTypeReflector.reflect_type(obj)
```

That call is not expected to appear in the deepest inner loops, but it is on the top-level path of important APIs. For
example, marshal calls like:

```python
msh.unmarshal(some_dict, ta.Sequence[Foo])
```

immediately reflect the user-provided type form. Even if the actual marshaler factory work is cached, the public API
entry point still pays the reflection lookup cost on every call. That means the trivial and common cases must be very
cheap:

- reflecting a plain concrete class such as `int`, `str`, `Foo`;
- reflecting a module-global generic type form such as `ta.Sequence[Foo]`;
- reflecting reused compound forms such as `ta.Mapping[int, ta.Sequence[Foo]]`;
- reflecting top-level type forms supplied repeatedly to marshal, dependency injection, dataclass inspection, and
  generated-signature machinery.

The codebase already uses the common performance trick of storing nontrivial type forms in module globals so they are
not reconstructed in function bodies. The reflection system should reward that pattern. If the same runtime object is
passed repeatedly, cache hits should be by object/key lookup rather than re-walking `typing` internals.

## Runtime Typing Object Reality

Runtime `typing` objects are ephemeral in principle and implementation-specific in practice.

CPython often internally caches parameterized typing forms. In practice, repeated construction of something like:

```python
ta.Sequence[Foo]
```

may return a reused object, but that behavior is an implementation detail and not a correctness foundation. Even when it
does happen, constructing those runtime forms can itself be expensive enough that performance-sensitive code avoids
doing it repeatedly.

This gives the reflection layer two separate jobs:

- exploit identity/object reuse when the caller has already arranged for stable runtime type objects;
- remain correct and fail-closed when equivalent type forms arrive as distinct runtime objects or freshly reflected IR.

Those are not the same problem and should not be collapsed into one cache.

## Concrete Use Cases

### Marshal Entry Points

The marshal system has a top-level user-facing path where a runtime type form is reflected before looking up a marshaler
or unmarshaler.

The fine-grained marshaler factories only run after a typecache miss. Those factories may inspect unions, literals,
generic arguments, dataclass fields, namedtuple fields, protocols, and other shapes. That work can be somewhat slower
because it is normally bootstrapping a cached marshaler.

The initial `reflect_type` call is different. It happens even when the marshaler itself is already cached. That makes
the reflection cache for simple and reused type forms especially important.

### Marshal Type Caches

The old marshal system uses a cache shaped roughly like:

```python
dict[rfl.Type, Marshaler]
```

The new system cannot rely only on Python object identity forever, because runtime reflection can produce equivalent but
not identical IR nodes. For supported shapes, `type_key` exists to provide explicit structural keys. This is useful for
marshal caches that need `list[int]` reflected twice to resolve to equivalent cache entries.

However, type keys are intentionally not a universal answer yet. They currently fail closed for unsupported recursive
forms and some advanced shapes. That is the right default while recursive aliases and alpha-equivalent type variable
semantics are still incomplete.

### Dataclass Generic Initializers

The custom dataclasses system uses reflection to reify generic field annotations in generated `__init__` methods. A
classic example is:

```python
class Box[T]:
    v: T

class IntBox(Box[int]):
    pass
```

The generated `IntBox.__init__` should expose `v: int`, not `v: T`. That requires:

- finding dataclass fields;
- finding the owner class for each field;
- building a generic-aware MRO;
- mapping owner type variables to concrete arguments;
- substituting those arguments into field annotations;
- optionally emitting runtime annotations for generated signatures.

That inspection work is not as hot as a bare `reflect_type(int)` call, but it is expensive enough to cache per
reflector/universe, especially because generated init and dependency-injection machinery may ask the same questions
repeatedly.

### Dependency Injection And NewType

The injector machinery needs `NewType` identity, not just the underlying supertype. Reflecting:

```python
UserId = ta.NewType('UserId', int)
```

as plain `int` loses information that injector dispatch may care about. The current system now reflects `NewType`
objects as distinct nominal `Instance` values with their own `TypeInfo`, while recording the supertype as a base where
possible.

This has caching consequences:

- `NewType` objects are runtime objects and should be cached by their object identity;
- their `TypeInfo` should be stable within a `RuntimeTypeUniverse`;
- runtime annotation emission should be able to recover the original `NewType` object;
- equivalent-looking `NewType`s with the same display name must remain distinct if they are distinct runtime objects.

### Recursive Use Cases

Some existing marshal users need recursive type support. The old system handles this through an escape hatch: users can
install a reflection override that bypasses normal `rfl.typeof`, returns an arbitrary sentinel, and then install a
custom factory that recognizes the sentinel and manually closes the recursive loop.

That escape hatch can continue to work in an adapter layer for a while, but the long-term goal is native recursive type
support. The new system should eventually support recursive aliases, recursive structural keys, and equivalence for
recursive types directly.

This matters for cache design. A future cache key scheme must be amenable to:

- recursive aliases;
- cyclic type graphs;
- alpha-equivalent type variables in corresponding positions;
- type variables with different runtime names but equivalent binding positions;
- coinductive equality or whatever mypy-equivalent recursive comparison strategy is ultimately adopted.

Until that exists, recursive and unsupported forms should fail closed rather than silently becoming unstable cache keys.

## Current Cache State

The current implementation has two strong-ref cache layers.

### Reflection Cache

`RuntimeTypeReflector` has a per-reflector cache:

```python
dict[object, Type]
```

This is used by `reflect_type`.

The behavior is intentionally simple:

- if the runtime object is hashable and already present, return the cached reflected `Type`;
- if the runtime object is hashable and not present, reflect it and store it;
- if the runtime object is unhashable, skip the cache and reflect it directly.

This gives good behavior for simple concrete types, `typing` aliases that are hashable, `NewType` objects, `TypeVar`
objects, and module-global type forms.

The cache is per `RuntimeTypeReflector`, not global. That is important because a reflector carries:

- a reference to a `RuntimeTypeUniverse`;
- a forward-reference resolver;
- type variable namespace/id allocation;
- dynamic type naming behavior through the referenced universe;
- runtime class and dynamic type identity assumptions through the referenced universe.

Sharing a universe across reflectors is valid and useful when they should agree on nominal `TypeInfo` identity. Sharing
reflected nodes across reflectors is a separate question and would currently be wrong or at least very easy to make
wrong.

### Inspection Cache

`RuntimeTypeReflector` now also has a small per-reflector inspection cache:

```python
dict[tuple[str, object], object]
```

It is used by the expensive runtime inspection surfaces:

- dataclass inspections;
- namedtuple inspections;
- record inspections;
- member inspections;
- protocol inspections.

This cache is colder than the reflection cache. Its main job is to avoid repeating expensive introspection and generic
substitution work when the same reflector asks the same high-level question about the same runtime object.

The cache key uses a string kind plus the inspected object. Examples are conceptually:

```python
('dataclass', Box[int])
('members', SomeClass)
('protocol', SomeProtocol[int])
```

If the object is unhashable, the cache is skipped. This mirrors `reflect_type`.

The current inspection cache is intentionally provisional. It gives useful behavior for repeated calls under one
reflector, but it is not the final thread-safe or structurally-keyed design.

### Runtime Universe Strong References

`RuntimeTypeUniverse` also keeps strong mappings for runtime classes and `NewType` objects:

- object to fullname;
- fullname to object;
- fullname to `TypeInfo`.

This is deliberate for now. Weakrefs and lifetime behavior are punted. Anonymous or dynamic classes, classes created by
decorators/metaclasses, and `NewType` objects are all retained strongly once the universe has seen them.

That is acceptable for the current direction because universes are explicit runtime objects. A long-running process can
choose a long-lived universe, while tests and short-lived tools can construct fresh universes.

## What The Current Caches Do Not Solve

The current caches do not solve several important problems.

### They Are Not Thread-Safe

The caches are plain dictionaries. Under normal GIL CPython this is often practically fine for simple workloads, but the
project explicitly cares about multithreaded and free-threaded/nogil CPython.

Under PEP 703-style free-threaded Python, unsynchronized mutable dictionaries shared across threads should not be
treated as a final design. The current state should be considered single-thread-oriented or externally synchronized.

### They Are Not Weakref-Aware

Everything is strong-ref for now.

This means a universe or reflector can extend the lifetime of runtime classes, dynamic classes, `NewType` objects,
typing aliases, reflected IR nodes, and inspection results. That is an explicit tradeoff for the current phase.

Weakref behavior is deferred because it interacts with:

- hashability and weakref support of runtime typing objects;
- dynamic classes and metaclass-created classes;
- deterministic test names;
- runtime type identity;
- cache invalidation semantics;
- thread safety.

### They Are Not Structural Reflection Caches

The reflection cache keys by runtime object, not by structural meaning.

If two different runtime objects represent equivalent type forms, the cache may reflect both. This is fine for the hot
identity path, but it does not replace `type_key` or future recursive canonicalization.

### They Do Not Cache Type Operations

Subtype checks, equivalence checks, joins, meets, substitution, type key construction, protocol compatibility, and other
algorithm-heavy operations are not broadly memoized yet.

Those operations should probably get their own caching strategy rather than sharing the runtime reflection cache. Their
correct keys and invalidation assumptions are different.

### They Do Not Solve Recursive Keys

Recursive aliases and recursive type graphs still need a real design. The current `type_key` surface deliberately fails
closed for recursive aliases rather than pretending to have a stable key.

That is important. Returning an unstable key for recursive forms would poison downstream caches in ways that are much
harder to debug than a clear failure.

## Cache Boundaries

The useful mental model is three cache families.

### 1. Runtime Reflection Cache

This is the hot path:

```python
runtime object -> Type
```

It should optimize:

- concrete classes;
- `NewType` objects;
- type variables;
- runtime aliases that are reused as module globals;
- common `typing` and builtin generic aliases.

It should stay per-reflector unless there is a very strong reason to globalize it. The reflector carries too much
semantic context to make global reflected nodes obviously safe.

### 2. Runtime Inspection Cache

This is the colder introspection path:

```python
runtime object + inspection kind -> inspection result
```

It should optimize:

- dataclass field surfaces;
- namedtuple field surfaces;
- normalized record surfaces;
- class member surfaces;
- protocol member surfaces;
- possibly protocol implementation diagnostics or successful compatibility checks later.

These results are coupled to the reflector/universe because they contain reflected `Type` nodes, type keys, runtime
annotation output, and generic substitutions. Per-reflector caching is the conservative default.

### 3. Type Operation Cache

This is the algorithmic path:

```python
Type operation + Type operands -> result
```

Examples include:

- `is_subtype(left, right)`;
- `is_same_type(left, right)`;
- alpha-equivalence;
- joins and meets;
- substitution;
- protocol compatibility;
- type key construction.

This cache family probably needs a more deliberate design because operands may be recursive, may be freshly constructed,
and may or may not have stable structural keys.

## Thread-Safety State

The current state is not thread-safe by design.

Current mutable shared state includes:

- `RuntimeTypeReflector._cache`;
- `RuntimeTypeReflector._inspection_cache`;
- `RuntimeTypeReflector._prepared_infos`;
- `RuntimeTypeReflector._resolving_forward_refs`;
- `RuntimeTypeReflector._next_type_var_id`;
- `RuntimeTypeUniverse._infos_by_fullname`;
- `RuntimeTypeUniverse._fullnames_by_type`;
- `RuntimeTypeUniverse._types_by_fullname`;
- `RuntimeTypeUniverse._next_dynamic_type_index`;
- mutable fields on `TypeInfo` such as bases and MRO during setup.

Under GIL CPython, many races are unlikely in normal single-threaded construction and then read-mostly use. Under nogil
CPython, that assumption is not enough.

The most obvious races are:

- two threads reflecting the same runtime object and both trying to populate `_cache`;
- two threads assigning dynamic names to new classes;
- two threads creating the same `TypeInfo`;
- one thread observing a partially configured `TypeInfo`;
- two threads allocating runtime type variable ids;
- two threads resolving forward refs through the same reflector;
- one thread reading an inspection result while another is populating related universe state.

No current tests model those races.

## Future Thread-Safe Directions

Thread safety should be added deliberately, not incidentally.

### Cache Abstraction

A small internal cache abstraction would let call sites remain simple while the implementation changes underneath.

Useful operations would be limited:

- get existing value;
- get-or-compute;
- maybe clear;
- maybe expose size for tests/debugging.

That abstraction could start as a dict wrapper and later gain locks or copy-on-write behavior.

### Coarse Locks First

The first real thread-safe implementation should probably use coarse locks.

Candidates:

- one lock on `RuntimeTypeReflector` protecting reflection cache, inspection cache, forward-ref state, prepared info
  state, and type variable id allocation;
- one lock on `RuntimeTypeUniverse` protecting dynamic name assignment, object/fullname mappings, and `TypeInfo`
  construction.

This will not be the fastest possible design, but it is much easier to make correct. Since reflection and inspection are
not intended to be deep inner-loop operations, coarse locks may be acceptable for a long time.

### Avoid Holding Locks Through User Code

Forward-reference resolution can call user-provided code. Future locking must avoid holding internal locks while calling
the resolver if possible.

Otherwise, user code could re-enter the reflector or universe and deadlock. This is especially relevant once recursive
aliases and recursive forward references become more capable.

### Publish Fully Initialized Objects

For nogil correctness, the universe should avoid publishing partially configured `TypeInfo` objects.

The current implementation stores a `TypeInfo` and then configures known bases/MRO. That is simple but not ideal for
concurrent readers. A future version should either:

- hold the universe lock until the `TypeInfo` is fully configured; or
- build a complete local object graph and publish it once; or
- use an explicit placeholder/initialization state that readers understand.

The first option is likely the pragmatic initial thread-safe version.

### Read-Mostly Optimization Later

If coarse locks become a bottleneck, later options include:

- double-checked cache lookup with locked population;
- immutable snapshot maps with copy-on-write updates;
- sharded locks by cache kind;
- per-thread reflectors sharing a read-only universe;
- a frozen universe mode after warmup.

Those are later optimizations. The immediate goal should be correctness under concurrent use, not lock-free cleverness.

## Interplay With Mypyc

The algorithm-heavy core is intended to remain mypyc-compatible. Runtime reflection is less constrained, but should stay
separate.

Caching complicates this boundary:

- core type operations may eventually want mypyc-friendly memoization;
- runtime reflection caches may use dynamic Python features and locks;
- shared cache abstractions should not force dynamic runtime behavior into the core;
- if the core gets compiled, any cache keys crossing the core/runtime boundary must remain simple and explicit.

This suggests keeping runtime caches in `runtime/` and adding any core operation caches separately in core modules, with
small simple data structures.

## Design Biases

The current direction should keep these biases:

- cache by identity/object first for the hot runtime path;
- use structural keys only where their semantics are explicit and fail-closed;
- keep caches per reflector/universe for now;
- keep all references strong for now;
- do not pretend unsupported recursive forms have stable keys;
- do not globalize caches until reflector/universe context has a clear equivalence model;
- make thread safety a first-class later pass, not a side effect of incidental dict use.

## Current Test Coverage

Current tests cover:

- repeated reflection returning the same IR object for the same runtime type object;
- repeated dataclass, namedtuple, record, member, and protocol inspection returning cached inspection objects under the
  same reflector;
- `NewType` identity preservation through reflection and runtime annotation emission;
- `Annotated` metadata preservation through reflection, type keys when metadata is hashable, and runtime annotation
  emission;
- fail-closed `Annotated` type keys when metadata is unhashable;
- protocol diagnostics for multiple simultaneous issues;
- protocol diagnostics for concrete unkeyable members.

Current tests do not cover:

- concurrent reflection;
- concurrent universe population;
- weakref/lifetime behavior;
- recursive structural cache keys;
- alpha-equivalent variable structural keys;
- operation-level memoization.

## Near-Term Guidance

The next caching work should probably be discussion/design before more implementation.

Good questions to settle before expanding the code are:

- Should inspection caches live on the reflector permanently, or should some move to the universe?
- Which public operations need cache identity guarantees versus only performance hints?
- Should `type_key` results themselves be cached on reflected nodes, in a side cache, or not yet?
- What is the first acceptable locking model for nogil correctness?
- Do we want a tiny cache abstraction now so locks can be added without editing every runtime module later?
- How should recursive alias placeholders interact with cache population?
- What escape-hatch compatibility is needed for current marshal recursive sentinel users while native recursive support
  is still incomplete?

The current implementation is useful, but provisional. It improves repeated-call behavior for current runtime surfaces
and preserves important identity semantics, while leaving room for a more explicit thread-safe cache design.
