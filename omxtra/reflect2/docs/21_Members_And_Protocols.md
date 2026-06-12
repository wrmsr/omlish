# Members And Protocols

This checkpoint covers the runtime member and protocol inspection work added after the runtime surface for marshal.

## Member Inspection

`runtime.members` is now the separate path for class namespace members. This keeps descriptor-backed methods and class
attributes distinct from the data-field-focused `runtime.records` layer.

The member surface currently classifies:

- normal functions;
- staticmethods;
- classmethods;
- properties;
- class data members.

Inspection uses static lookup so descriptors are classified without binding or executing them.

Members carry the raw `inspect.Signature` when one is available. They also carry a reflected signature whose parameter
and return annotations have been converted to the internal type IR. Missing annotations are reflected as omitted `Any`.

## Call And Value Views

The stored reflected signature remains unbound. Separate helpers expose descriptor-aware views:

- instance methods drop `self` for public call signatures;
- classmethods drop `cls`;
- staticmethods keep their parameters unchanged;
- properties expose a value type instead of a call signature;
- ordinary data members do not get a call signature.

This preserves the distinction between a callable value stored as data and a descriptor-backed method on the class.

## Generic Member Substitution

Member signatures now receive generic substitutions in the inspected class context. Examples now supported include:

- `Box[int].get(self) -> T` reflecting a public return type of `int`;
- `Box[int].put(self, value: T) -> None` reflecting a public parameter type of `int`;
- inherited methods from `Box[T]` on `StrBox(Box[str])` reflecting `str`.

Unparameterized generic classes currently follow the runtime reflector behavior and use omitted generic arguments as
`Any`.

## Member Keys

Member signatures can now be keyed structurally:

- public call signatures have stable keys;
- property value types have stable keys;
- unsupported or unkeyable reflected types fail closed.

This mirrors the type-key work for fields and gives dependency injection, protocol lookup, and cache code an explicit
comparison primitive without relying only on object identity.

## Protocol Inspection

`runtime.protocols` adds protocol member inspection without doing protocol conformance checking yet.

It currently supports:

- protocol detection;
- method and property members through the member inspection machinery;
- annotation-only protocol data members;
- generic protocol substitution, such as `BoxLike[int]`;
- inherited protocol members;
- protocol member keys.

Protocol member keys reuse member call/value keys. Method-like members key by public call signature. Data-like members
key by value type.

## Boundaries

This is still inspection, not checking.

The system does not yet decide whether a concrete class conforms to a protocol. It also does not yet implement:

- variance-aware protocol matching;
- overloaded members;
- property setter/deleter semantics;
- recursive protocols;
- `@runtime_checkable` behavior;
- descriptor-specific edge cases beyond the first call/value distinction.

The next natural implementation step is a very small protocol-conformance predicate based on exact member-key matching,
with fail-closed behavior for unsupported members.

## Test State

The full package test suite currently passes with 499 tests.
