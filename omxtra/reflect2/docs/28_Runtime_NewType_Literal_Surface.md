# Runtime NewType Literal Surface

This checkpoint records the runtime reflection work after `27_Near_Term_Fundamentals.md`.

The main theme of this stretch was turning the low-level runtime reflection pieces into a more coherent
marshal/DI-oriented surface, without introducing a polished public facade yet. The package still exposes small focused
runtime modules, but the tests now demonstrate that a user can reflect real runtime type forms, preserve nominal
identity where it matters, inspect effective shapes, and get stable keys suitable for cache lookup.

## Cache Semantics

The reflector cache behavior is now covered more directly.

Reflection caches hashable runtime forms and skips unhashable runtime forms. For example, an unhashable
`Annotated[int, []]` form still reflects successfully, but it is not stored in the runtime-object cache.

Runtime annotation emission caches successful conversions and does not cache failures. This matters because an
unsupported IR node should fail closed every time, rather than poisoning later calls with a stale sentinel.

Type-key caches now have explicit tests for both successful keys and `None` from optional key APIs. Calling
`type_key_or_none` on an unsupported node can cache `None`, but `type_key` still raises and does not populate the
positive key cache.

Inspection caches are pinned as per-reflector. Dataclass, namedtuple, record, member, and protocol inspections reuse
results inside one reflector and do not share across separate reflectors. The low-level `cached_inspection` helper is
also covered for:

- unhashable source objects;
- distinct `kind` values for the same object;
- fail-open behavior where unhashable inspection keys simply rerun the factory.

The implementation is still single-thread-oriented. These are strong-ref dict caches, not the final thread-safe or
nogil-safe cache design.

## Literal Values

Literal support has been aligned across reflection, type keys, runtime annotation emission, query helpers, and dispatch
summaries.

Runtime reflection now accepts:

- `bool`;
- exact `int`;
- `str`;
- `bytes`;
- `float`;
- `None`.

String type keys inline the small stable scalar set:

- `None` as `None:`;
- `bool`;
- exact `int`;
- `str`;
- `bytes`.

Floats remain reflectable but opaque in type keys. This keeps the runtime reflection surface broad enough for existing
Python forms while keeping compact string keys conservative.

`Literal[None]` is distinct from plain `NoneType`. Runtime `None` and `type(None)` both reflect to the `NoneType` node
and key as `None`, while `Literal[None]` keys as:

```text
L[None:,I['builtins.None']]
```

The runtime universe now treats `type(None)` as the known runtime type `builtins.None` so literal fallbacks are stable
instead of dynamic names.

Union keys for literal forms are order-insensitive, including mixed stringable and opaque literal members. Opaque
literal union members are placed in the explicit `OU[...]` bucket so a union of opaque literal children cannot collide
with a literal frozenset payload.

Tests now cover:

- byte literal reflection and dispatch;
- float literal reflection and opaque keys;
- `None` literal reflection and keys;
- literal value extraction;
- homogeneous literal value type queries;
- mixed literal value type rejection;
- runtime annotation round trips;
- runtime dispatch summaries for byte, float, and `None` literals.

## NewType Identity

`NewType` preservation is now a first-class runtime use case.

The runtime universe already retained the original `NewType` object as the runtime object for the nominal `TypeInfo`.
The recent work built out the tests and query expectations around that.

Important behavior now pinned:

- annotation emission for a reflected `NewType` returns the original `NewType` object;
- two different `NewType`s over the same supertype have distinct type keys;
- a `NewType` key differs from the key of its supertype;
- `RuntimeTypeShape` exposes both the nominal `NewType` identity and the effective reflected supertype;
- dispatch uses the effective supertype while keeping the original and NewType metadata.

This is especially important for injector-style code: the annotation-facing surface must preserve the nominal type,
while marshal-style code must be able to inspect the effective runtime shape underneath it.

One boundary is explicit: `TypeInfo.bases` is only populated for NewTypes whose supertype is an instance-like runtime
class. For non-instance supertypes such as `Literal[...]`, raw `TypeInfo.bases` remains empty. Callers should use the
runtime query surface to recover the supertype facts.

## NewType And Literals

The main new practical capability is `NewType` over literal-bearing forms.

Covered examples include:

```python
Mode = NewType('Mode', Literal['a', 'b'])
MaybeMode = NewType('MaybeMode', Literal[None, 'x'])
```

The runtime query layer preserves:

- `Mode` as the nominal annotation;
- `Literal['a', 'b']` as the effective supertype;
- literal value facts such as `('a', 'b')`;
- distinct keys for `Mode` and `OtherMode` even when both have the same literal supertype.

`MaybeMode` is also covered. Its effective supertype is a mixed literal union, so it does not collapse into a simple
homogeneous `LiteralValueType`, and it is not treated as an optional shape merely because one literal value is `None`.

## Record-Like Surfaces

Dataclass, namedtuple, and unified record inspection now have focused coverage for NewType/literal fields.

Direct fields preserve the NewType annotation:

```python
Mode = NewType('Mode', Literal['a', 'b'])

@dataclass
class Config:
    mode: Mode
```

The reflected field type is the NewType node. Calling `get_runtime_type_shape` on that field type exposes the effective
literal values.

Inherited generic replacement is covered as well:

```python
@dataclass
class Box[T]:
    value: T

class ModeBox(Box[Mode]):
    pass
```

The replaced field annotation for `ModeBox` is `Mode`, not the literal supertype. Field keys for `Box[Mode]` and
`Box[OtherMode]` remain distinct.

The same behavior is covered for generic `NamedTuple` records and the unified `inspect_record` surface.

## Members And Protocols

Method signature inspection now has explicit coverage for NewType/literal parameters and return types.

Direct methods preserve the nominal annotation:

```python
def set_mode(self, mode: Mode) -> Mode: ...
```

The reflected call signature can emit `Mode` again through `to_runtime_annotation`, and shape queries on the parameter
or return type expose the literal values underneath.

Inherited generic methods are covered:

```python
class Box[T]:
    def get(self) -> T: ...
    def put(self, value: T) -> T: ...

class ModeBox(Box[Mode]):
    pass
```

The member inspection path substitutes `T` to the NewType in both parameter and return positions.

Protocols now have matching coverage. Protocol method signatures and data members preserve NewType identity. Protocol
checking accepts concrete implementations using the same NewType and rejects implementations using a different NewType
with the same literal supertype. This pins that protocol keys compare the nominal type, not just the effective
literal shape.

## Runtime Type Aliases

Non-recursive runtime `TypeAliasType` values currently expand during reflection and runtime annotation emission.

This is now covered deliberately. For example:

```python
Mode = NewType('Mode', Literal['a', 'b'])
ModeList = TypeAliasType('ModeList', list[Mode])
```

Reflecting or emitting `ModeList` produces the expanded runtime form `list[Mode]`. The alias identity itself is not
preserved for non-recursive aliases today.

Generic aliases are covered too:

```python
T = TypeVar('T')
BoxAlias = TypeAliasType('BoxAlias', list[T], type_params=(T,))
```

`BoxAlias[Mode]` emits as `list[Mode]`, and collection-shape queries expose `Mode` as the item type. Keys for
`BoxAlias[Mode]`, `BoxAlias[OtherMode]`, and `BoxAlias[Literal['a', 'b']]` remain distinct after expansion.

This behavior is covered across direct annotation emission, collection queries, dataclass fields, and method
signatures.

Recursive aliases are unchanged: recursive `TypeAliasType` values still reflect as alias nodes and remain governed by
the existing stack-relative recursive key model.

## Integrated Runtime Surface

`runtime/tests/test_surface.py` now contains a compact end-to-end workflow showing what users can do today with a
single reflector:

- reflect a NewType over a literal supertype;
- inspect a generic dataclass field specialized with that NewType;
- emit runtime annotations preserving the NewType object;
- query effective literal shape;
- inspect a method using the NewType;
- inspect and check a protocol using the NewType;
- compare keys against a different NewType with the same supertype;
- observe cache reuse across repeated reflection and inspection calls.

This is not a final public API. It is an executable capability statement for the current runtime reflection toolbox.

## Immediate Goals

The next immediate work should stay focused on fundamentals and marshal/DI-facing capability rather than API polish.

Likely next steps:

- add equivalent alias/NewType/literal coverage for protocols where aliases appear in protocol annotations;
- add tests for nested collection dispatch such as `Mapping[str, list[Mode]]`, including NewType literal item shapes;
- add small helper queries only where repeated tests show real caller friction, not as a broad facade;
- audit fail-closed behavior for alias expansion failures in dataclass/member/protocol inspection;
- add cache tests for aliases and NewTypes to ensure repeated module-global forms hit reflector caches predictably.

## Mid-Term Goals

The larger direction remains unchanged from the original intent.

Important mid-term goals:

- design the real recursive alias/type-key model, including mutually recursive aliases and alpha-equivalent variables;
- improve callable and overload operations beyond the current bounded callable subtype slice;
- decide how member-signature keys should relate to the shared type-key writer model;
- build a thin experimental adapter that can mimic the old reflection system's marshal-facing facts without depending
  on higher-level packages;
- revisit thread-safe cache design for shared reflectors under free-threaded Python;
- keep core IR and algorithm-heavy code mypyc-friendly, while runtime inspection code may remain less constrained.

Nice-to-have but lower priority:

- improve alias preservation for non-recursive runtime aliases if a concrete user needs alias identity;
- broaden literal value support for compound literal payloads if real code requires it;
- add more mypy-derived operation semantics around protocols, overloads, and callable assignability.

The current system is now meaningfully useful at runtime for a narrow but important path: runtime forms involving
NewType, Literal, generic records, members, protocols, aliases, runtime annotation emission, type keys, and per-reflector
cache reuse.
