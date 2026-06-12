# Runtime Reflector Entry Points

Runtime reflection can be used through a few layers.

For quick reflection of simple or known type forms, the module-level helper uses
the default global reflector:

```python
reflect_type(list[int])
```

For application work, prefer creating an explicit reflector and reusing it:

```python
reflector = make_runtime_reflector(
    dynamic_type_name_suffix=DYNAMIC_TYPE_NAME_ID,
    forward_ref_resolver=resolver,
)
```

The factory wires together a `RuntimeTypeUniverse` and a `RuntimeTypeReflector`.
It exposes the common runtime knobs without forcing callers to manually compose
both objects.

Pass that same reflector into runtime operations:

```python
reflect_type_str(UserType, reflector)
reflect_is_same_type(left, right, reflector)
reflect_mro_instances(Child[int], reflector)
reflect_substitute_type(list[T], {T: int}, reflector)
```

Reusing a reflector matters because it owns:

- the runtime reflection cache,
- the runtime universe and dynamic `TypeInfo` identities,
- runtime `TypeVar` identity mapping,
- forward reference resolution state.

Avoid mixing reflectors for related operations when dynamic class identity or
runtime TypeVar identity matters. Two different reflectors may produce distinct
`TypeInfo` or `TypeVarType` objects for the same runtime inputs, which can
change strict comparison, substitution, and generic base mapping behavior.

The default reflector is still useful for small one-off operations. Application
code should usually keep an explicit reflector per logical reflection context.
