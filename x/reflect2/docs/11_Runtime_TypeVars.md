# Runtime TypeVars

Runtime `TypeVar` handling is now explicit enough to document as a boundary.
The runtime reflector accepts `typing.TypeVar` objects and turns them into core
`TypeVarType` nodes. Those nodes preserve the runtime object's name, variance,
constraints, and upper bound where Python exposes them.

Runtime TypeVars are identity-based. Two separate calls to `TypeVar('T')`
produce distinct runtime objects, and the reflector gives them distinct
`TypeVarId` values even though their names match. Reflecting the same runtime
object through the same reflector returns the same reflected node from the
reflector cache.

That gives the current comparison contract:

- `reflect_is_same_type(list[T], list[T])` is true when both aliases contain the
  same runtime `T` object.
- `reflect_is_same_type(list[T], list[U])` is false when `T` and `U` are
  different runtime objects, even if both are named `T`.
- `reflect_is_alpha_equivalent(list[T], list[U])` is the explicit operation for
  same-shape types with different TypeVars in equivalent positions.

Substitution follows the same identity rule. A runtime substitution map such as
`{T: int}` replaces occurrences of that exact runtime `T`; it does not replace
another same-name `TypeVar('T')`.

Examples:

```python
T = typing.TypeVar('T')
U = typing.TypeVar('T')

reflect_type_str(reflect_substitute_type(dict[T, U], {T: int}))
# builtins.dict[builtins.int, T]

reflect_is_same_type(list[T], list[U])
# False

reflect_is_alpha_equivalent(list[T], list[U])
# True
```

`ParamSpec` and `TypeVarTuple` are not reflected yet. They currently fail closed
with `UnreflectableTypeError`, leaving room to model them deliberately later
instead of accidentally treating them like ordinary TypeVars.

This is not the final recursive/canonical comparison story. The current shape
keeps strict runtime identity, explicit alpha-equivalence, and future expansion
separate so later de Bruijn-style or canonical naming work can be added without
changing the meaning of strict comparison.
