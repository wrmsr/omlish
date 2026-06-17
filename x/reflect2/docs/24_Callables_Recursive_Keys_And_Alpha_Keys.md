# Callables Recursive Keys And Alpha Keys

This checkpoint covers the runtime reflection and keying work added after the caching/threading checkpoint.

## Overview

The work after `23_Caching_And_Threads.md` focused on two practical gaps that block replacing more of the old runtime
reflection system:

- richer callable reflection and runtime annotation emission;
- recursive and alpha-equivalent structural keys for cache use.

The direction remains conservative. Exact identity-sensitive keys still exist, and the newer alpha-equivalent keys are a
separate API. Unsupported shapes should still fail closed rather than produce unstable cache entries.

## Housekeeping

Runtime tests now live beside the runtime package code under `runtime/tests`. This keeps the tests for reflection,
runtime operations, members, records, protocols, and annotation emission close to the implementation surface they cover.

Runtime known-name tables were also split into `runtime/known.py`, which leaves `runtime/universe.py` focused on
universe state, dynamic nominal identity, and runtime `TypeInfo` construction.

The wording in `23_Caching_And_Threads.md` was tightened around `RuntimeTypeUniverse` and `RuntimeTypeReflector`
relationships. A reflector carries a reference to a universe; it does not inherently own that universe. Sharing a
universe across reflectors is valid when callers want nominal `TypeInfo` identity to be shared. Sharing reflected nodes
or reflector-local caches is a separate question and is still not assumed safe.

## Callable Reflection

Runtime `typing.Callable` forms now support more than positional argument lists and ellipsis.

The reflector now handles:

- `Callable[[A, B], R]`;
- `Callable[..., R]`;
- `Callable[P, R]` where `P` is a `ParamSpec`;
- `Callable[Concatenate[A, B, P], R]`.

`Callable[P, R]` is represented internally as a `CallableType` with two synthetic trailing parameters:

- `*args: P`;
- `**kwargs: P`.

`Callable[Concatenate[A, B, P], R]` is represented as positional prefix parameters followed by the same synthetic
`ParamSpec` `*args/**kwargs` pair.

This mirrors the useful mypy shape closely enough for runtime reflection and keying, without trying to model every
checker-level callable feature yet.

## Callable Boundaries

Keyword-only arguments, argument defaults, and named argument details are available from runtime member inspection via
`inspect.signature`. They are not generally expressible in a plain runtime `typing.Callable[...]` object.

The runtime annotation emitter therefore now fails closed when asked to emit a `CallableType` shape that
`collections.abc.Callable[...]` cannot represent accurately. In particular, named and keyword-only parameter shapes are
not silently flattened into positional callables.

This is important for generated signatures and dependency-injection integration. Losing keyword-only or default-shape
information would be worse than raising clearly.

## Runtime Annotation Emission

`RuntimeTypeReflector` now exposes:

```python
reflector.to_runtime_annotation(typ)
```

This wraps `runtime.annotations.to_runtime_annotation` with reflector-local context and caching.

The reflector context matters because some runtime annotation emission needs more than a `RuntimeTypeUniverse`.
Specifically:

- runtime `TypeVar` and `ParamSpec` objects need to be recovered from reflected `TypeVarLikeType` nodes;
- `ParamSpec` and `Concatenate` callable forms need those original runtime parameter objects;
- `NewType` emission needs the universe's runtime-object reverse lookup;
- recursive and generic forms should use the same reflector state that produced the IR.

The annotation cache is currently per reflector and keyed by reflected `Type` object identity. This follows the same
provisional cache direction as the reflection and inspection caches: useful now, strong-ref only, and not yet the final
thread-safe cache abstraction.

The lower-level `to_runtime_annotation` function still exists. It accepts an optional type-variable resolver and remains
fail-closed when it does not have enough context.

## Overloaded Members

Runtime member inspection now collects overload signatures registered through `typing.overload`.

The implementation uses `typing.get_overloads` only for actual overloadable objects and ignores ordinary class data
members. It still does not peer into arbitrary callable objects beyond what `inspect.signature` already provides.

This gives member and protocol machinery access to overload shape in a future-compatible way, while leaving overload
matching itself for later work.

## Recursive Runtime Aliases

Runtime `typing.TypeAliasType` reflection now preserves recursive aliases as `TypeAliasType` nodes rather than trying to
expand them indefinitely.

The covered shapes include:

- direct recursion such as `Alias = list['Alias']`;
- indirect recursion such as `A = list['B']` and `B = dict[str, 'A']`;
- parameterized recursion such as `Alias[T] = list['Alias[T]']`.

The runtime reflector tracks aliases currently being resolved. Forward references matching an active alias name become
alias backreferences. A limited `Alias[T]` string form is recognized when it refers to the active alias and its own
runtime type parameters.

This is intentionally not a general parser for arbitrary string annotations. It is a targeted bridge for common
recursive `TypeAliasType` forms.

## Recursive Type Keys

Exact `type_key` now supports recursive aliases.

Recursive aliases are keyed using stack-relative alias backreferences. For example, a direct alias recursion is keyed
conceptually as:

```text
recursive_type_alias(
  args=(),
  target=list[type_alias_ref(0, args=())],
)
```

Indirect recursive aliases work the same way, with nested aliases pushing additional stack frames.

Parameterized recursive aliases include the recursive reference's argument keys. This matters because:

```python
Alias[int]
```

and:

```python
Alias[str]
```

must not collide.

When keying a parameterized alias, the alias target is substituted before key construction. This keeps backreference
arguments concrete where possible.

## Alpha Keys

The exact `type_key` remains identity/id based for type variables. That is still useful for exact caches.

A new separate key family now exists:

```python
alpha_type_key(typ)
alpha_type_key_or_none(typ)
```

Runtime wrappers also exist:

```python
reflect_alpha_type_key(obj, reflector=None)
reflect_alpha_type_key_or_none(obj, reflector=None)
```

Alpha keys canonicalize type-var-like nodes by first occurrence:

- `TypeVarType`;
- `ParamSpecType`;
- `TypeVarTupleType`.

This allows equivalent variable shapes to key the same even when the underlying runtime variables differ.

Examples now covered:

- `list[T]` and `list[U]` alpha-key the same;
- `Pair[T, T]` alpha-keys like `Pair[U, U]`;
- `Pair[T, T]` does not alpha-key like `Pair[U, V]`;
- `Callable[[T], T]` alpha-keys like `Callable[[U], U]`;
- recursive aliases with different type variable identities can alpha-key the same.

Keeping this separate from exact `type_key` is deliberate. Marshal and dependency-injection caches may need different
key semantics at different boundaries.

## Current Cache Shape

Current runtime cache layers now include:

- runtime object to reflected `Type`, on `RuntimeTypeReflector`;
- inspection result cache, on `RuntimeTypeReflector`;
- reflected `Type` to runtime annotation, on `RuntimeTypeReflector`.

Type keys are not cached yet. The next small caching step is likely to add reflector methods for exact and alpha type
keys and cache those per reflected `Type` object.

That would avoid recomputing recursive keys repeatedly while keeping the cache policy local to the reflector.

## Remaining Boundaries

Several areas are still intentionally incomplete:

- full parsing of arbitrary string forward references;
- general recursive alias graph canonicalization beyond the tested structures;
- operation-level caches for subtype/equivalence/join/meet;
- variance-aware protocol checking beyond the current partial work;
- full overload matching;
- `Self` with class context;
- thread-safe cache implementation for free-threaded Python;
- final mypyc-oriented cache boundaries.

The important progress is that recursive aliases and alpha-equivalent variables are no longer purely theoretical. There
is now an explicit tested key surface that can be used by future marshal/cache work, while exact keys remain available
for identity-sensitive cases.

## Test State

The full package test suite now passes with 540 tests across core and runtime test packages.

Focused coverage now includes:

- callable `ParamSpec` and `Concatenate` reflection;
- callable runtime annotation emission and fail-closed unsupported callable shapes;
- reflector-local runtime annotation caching;
- overload signature collection;
- direct, indirect, and parameterized recursive alias reflection;
- recursive alias exact keys;
- alpha-equivalent keys for generic instances, callables, and recursive aliases;
- runtime wrappers for alpha keys.
