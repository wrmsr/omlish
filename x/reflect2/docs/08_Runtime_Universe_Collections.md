# Runtime Universe Collections

This note records the current synthetic collection metadata in the runtime universe.

## Why It Exists

Python's runtime class MRO does not include most `collections.abc` virtual base relationships.

For example, `issubclass(list, collections.abc.Sequence)` is true, but `Sequence` is not present in `list.__mro__`. If runtime reflection copied only `__mro__`, the distilled IR could not answer questions such as:

```python
reflect_is_assignable(list[int], Sequence[int])
reflect_base_args(list[int], Sequence)
```

The runtime universe therefore provides a small synthetic base graph for common builtin collections. Reflection preserves these richer synthetic MROs instead of overwriting them with the concrete runtime `__mro__`.

## Metadata Shape

Known collection metadata is table-driven in `runtime/universe.py`.

`_KNOWN_BASE_SPECS` describes declared base instances. Its argument specs are intentionally simple:

- an integer means "use this type variable from the current `TypeInfo`"
- a string means "use a concrete zero-argument instance with this fullname"

`_KNOWN_MRO_TAILS` describes synthetic nominal reachability for subtype checks. Each entry stores the MRO tail after the type itself.

This keeps the metadata audit-friendly as more known runtime relationships are added.

## Current Graph

Sequence-like relationships:

```text
str              -> Sequence[str] -> Iterable[str]
bytes            -> Sequence[int] -> Iterable[int]
list[T]          -> MutableSequence[T] -> Sequence[T] -> Iterable[T]
tuple[T]         -> Sequence[T] -> Iterable[T]
MutableSequence[T] -> Sequence[T] -> Iterable[T]
Sequence[T]        -> Iterable[T]
```

Mapping relationships:

```text
dict[K, V]            -> MutableMapping[K, V] -> Mapping[K, V] -> Iterable[K]
MutableMapping[K, V]  -> Mapping[K, V] -> Iterable[K]
Mapping[K, V]         -> Iterable[K]
```

Set relationships:

```text
set[T]          -> MutableSet[T] -> Set[T] -> Iterable[T]
frozenset[T]    -> Set[T] -> Iterable[T]
MutableSet[T]   -> Set[T] -> Iterable[T]
Set[T]          -> Iterable[T]
```

These are intentionally the common generic collection families already represented in the universe. They are not a complete model of every virtual ABC registration.

## Runtime Behavior

The graph feeds subtype, join/meet, assignability, and base argument extraction.

Examples now supported:

```python
reflect_is_assignable(list[int], Sequence[int])       # True
reflect_is_assignable(tuple[int, ...], Sequence[int]) # True
reflect_is_assignable(dict[str, int], Mapping[str, int]) # True
reflect_is_assignable(set[int], Set[int])             # True
reflect_is_assignable(frozenset[int], Set[int])       # True

reflect_base_args(list[int], Sequence)       # [int]
reflect_base_args(tuple[int, ...], Sequence) # [int]
reflect_base_args(dict[str, int], Mapping)   # [str, int]
reflect_base_args(set[int], Set)             # [int]
reflect_base_args(frozenset[int], Set)       # [int]
```

The `str` and `bytes` cases use concrete base arguments:

```python
reflect_is_assignable(str, Sequence[str])     # True
reflect_base_args(str, Sequence)              # [str]

reflect_is_assignable(bytes, Sequence[int])   # True
reflect_base_args(bytes, Sequence)            # [int]
```

## Boundaries

This is still not full ABC inference.

Current limitations:

- no scanning of runtime ABC registries
- no protocol or structural subtyping
- no special handling for user-defined virtual subclasses
- no complete model of every `collections.abc` relationship
- callable ABC behavior remains outside the implemented subtype fragment

The current graph is deliberately explicit and small. It should grow by adding targeted table entries with tests that show the runtime operation the relationship enables.
