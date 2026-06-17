# Instantiated Runtime MRO

The package now exposes the runtime equivalent of the old `generic_mro` style
operation.

Given a reflected instance such as `Child[int]`, the core helper can produce
the instantiated MRO entries with type variables remapped at each inheritance
layer:

```python
get_mro_instances(instance)
get_mro_instances_or_none(instance)
```

The runtime wrappers reflect Python runtime type objects first:

```python
reflect_mro_instances(Child[int], reflector)
reflect_mro_instances_or_none(Child[int], reflector)
reflect_mro_type_strs(Child[int], reflector)
```

For a hierarchy like:

```python
A = typing.TypeVar('A')
B = typing.TypeVar('B')
X = typing.TypeVar('X')
Y = typing.TypeVar('Y')

class Base(typing.Generic[A, B]):
    pass

class Middle(typing.Generic[X], Base[list[X], str]):
    pass

class Child(typing.Generic[Y], Middle[dict[str, Y]]):
    pass
```

`reflect_mro_type_strs(Child[int], reflector)` produces entries shaped like:

```text
Child@1[builtins.int]
Middle@2[builtins.dict[builtins.str, builtins.int]]
Base@3[builtins.list[builtins.dict[builtins.str, builtins.int]], builtins.str]
typing.Generic
builtins.object
```

The exact dynamic class prefix depends on the universe naming mode. In
counter mode, suffixes are deterministic in first-seen order. In default mode,
suffixes use runtime object identity.

The strict helpers raise if any MRO entry cannot be mapped. The `or_none`
variants return `None` for unsupported mappings, while still raising for inputs
that are not runtime class/instance type forms.

These helpers do not parse or inspect source. They use the reflected
`TypeInfo.mro`, `TypeInfo.bases`, and core substitution machinery.
