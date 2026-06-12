# Runtime Surface Refocus

This checkpoint covers the recent runtime-surface expansion after
`docs/17_Current_State_And_Roadmap.md`. The work stayed mostly in tests and
runtime-facing helpers, with one larger detour through `TypedDict` behavior.

## What Changed

The runtime entry point surface is now better covered by tests. A focused
entrypoint test module exercises:

- default `reflect_type()` behavior,
- `make_runtime_reflector()` configuration,
- explicit reflector reuse,
- runtime operation helpers over runtime type objects,
- fail-closed behavior for unreflectable inputs and wrong operation shapes.

The test suite also now has shared helper constructors for the core lattice and
subtype tests in `tests/helpers.py`.

## Runtime Reflection Additions

Reflection now covers several more Python 3.14 typing forms:

- `typing.Required[T]`,
- `typing.NotRequired[T]`,
- `typing.ReadOnly[T]`,
- `typing.TypedDict` runtime classes,
- generic `TypedDict` aliases,
- `typing.Unpack[T]` as a structural `UnpackType`.

`RequiredType` now mirrors mypy more closely by carrying a `required` flag, so
the same node can represent both `Required[T]` and `NotRequired[T]`.

`ParamSpec` and `TypeVarTuple` remain unsupported, but they now fail with
explicit error messages. This matters because `Unpack[Ts]` is easy to mistake
for supported variadic behavior. `Unpack[tuple[int, str]]` reflects
structurally; `Unpack[Ts]` still fails closed until real variadic machinery is
implemented.

## TypedDict Detour

The system can now reflect runtime `TypedDict` classes into `TypedDictType`.
It reads runtime metadata such as:

- `__annotations__`,
- `__required_keys__`,
- `__optional_keys__`,
- `__readonly_keys__`.

It also unwraps top-level `Required`, `NotRequired`, and `ReadOnly` item
markers into `TypedDictType.required_keys` and `TypedDictType.readonly_keys`.
Invalid nested marker positions fail closed.

Core operations now include conservative `TypedDict` support:

- structural subtype / assignability,
- join,
- meet.

This work was useful for exercising the IR and lattice behavior, but it is not
where the project should keep focusing right now. The primary application code
does not currently use `TypedDict`; it uses dataclasses and runtime class
hierarchies. Future `TypedDict` work should be demand-driven.

## Literal Support

Literal preservation is important for marshalling. The existing reflection of
`typing.Literal[...]` preserves values as `LiteralType`, and multi-value
literal forms become unions of `LiteralType` nodes.

New helpers make this information easier to consume:

- `get_literal_values()`,
- `get_literal_values_or_none()`,
- `reflect_literal_values()`,
- `reflect_literal_values_or_none()`.

These return finite literal value sets from a reflected type, preserving order.
Mixed literal/non-literal unions are treated as non-finite by the permissive
helper and raise in the strict helper.

There is also a narrow runtime helper for `TypedDict` item literals:

- `reflect_typed_dict_literal_values()`.

That helper is useful but should not pull the roadmap further toward
`TypedDict`. For dataclass-oriented marshalling, similar literal extraction
should happen over dataclass fields next.

## Current Runtime Value

At runtime, a caller can now:

- reflect common `typing` forms into the core IR,
- inspect generic class bases and instantiated MRO entries,
- substitute runtime `TypeVar` objects,
- compare strict or alpha-equivalent type shapes,
- ask assignability questions,
- compute conservative joins and meets,
- extract finite literal value sets,
- get per-field literal sets for `TypedDict` classes.

The system remains source-unaware and fail-closed. Unsupported reflection forms
raise `UnreflectableTypeError`; unsupported core operations raise
`UnsupportedTypeOperationError` or `TypeError` rather than returning misleading
answers.

## Refocus

The next phase should shift away from adding isolated `typing` corners and away
from more `TypedDict` helpers.

The better next target is dataclass and runtime class hierarchy reflection,
because that aligns with the intended marshalling use case:

- inspect dataclass fields,
- resolve field annotations through the existing reflector,
- preserve finite literal sets on fields,
- handle generic dataclasses through the existing generic-base machinery,
- fail closed for unresolved forward refs or unsupported annotation forms.

This should initially be a runtime helper layer, not a new core IR node. The
core already has the type forms needed to represent field annotations. The new
work should expose ergonomic runtime queries over dataclass classes while
keeping the core algorithm layer clean.

## Open Questions

Dataclass reflection needs a few concrete choices:

- Whether to include only real fields or also `InitVar` / `ClassVar`.
- Whether field order should be preserved as a list of entries rather than a
  dictionary.
- How much dataclass metadata to expose initially: defaults, default factories,
  `init`, `kw_only`, frozen-ness, and inherited fields.
- How to represent fields from generic dataclasses once a concrete runtime alias
  such as `Box[int]` is supplied.

The likely first increment is a small `DataclassField` runtime result object
with field name, reflected type, and a few basic dataclass flags. Literal value
extraction can then be layered on top of those reflected field types.
