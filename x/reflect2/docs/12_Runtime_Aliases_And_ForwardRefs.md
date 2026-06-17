# Runtime Aliases And Forward References

Python 3.14 `typing.TypeAliasType` is now reflected by expanding the alias value.
The runtime reflector does not currently preserve alias identity for these
runtime alias objects.

Concrete aliases are reflected as their targets:

```python
Alias = typing.TypeAliasType('Alias', list[int])

reflect_type_str(Alias)
# builtins.list[builtins.int]
```

Generic aliases are also expanded. When a runtime alias is subscripted, its
runtime type parameters are substituted into the alias target:

```python
T = typing.TypeVar('T')
Alias = typing.TypeAliasType('Alias', dict[str, T], type_params=(T,))

reflect_type_str(Alias[int])
# builtins.dict[builtins.str, builtins.int]
```

This is deliberately simpler than the core `TypeAliasType` IR node. The core IR
can represent alias identity and recursive aliases, while the runtime reflection
path currently treats Python runtime aliases as transparent type forms. That
keeps the first runtime behavior useful without pretending we have a full alias
symbol table.

Forward references fail closed by default. Raw string references,
`annotationlib.ForwardRef`, `typing.ForwardRef`, and alias values that contain
unresolved strings raise `UnreflectableTypeError` unless the caller supplies a
resolver.

Forward reference resolution is explicitly in-memory and user supplied:

```python
reflector = RuntimeTypeReflector(
    forward_ref_resolver=lambda name: {'User': int}[name],
)

reflect_type_str('User', reflector)
# builtins.int

reflect_type_str(list['User'], reflector)
# builtins.list[builtins.int]
```

The reflector does not inspect source files, module globals, locals, import
state, or annotation owner objects. A resolver receives only the forward
reference name and returns another runtime type object for normal reflection.
If the returned object is unsupported, the usual reflection error is propagated.

Recursive resolver loops fail closed with `UnreflectableTypeError` instead of
recursing indefinitely.
