# Runtime Universe Dynamic Names Implemented

Dynamic runtime type naming is now implemented in `RuntimeTypeUniverse`.

Known runtime types keep stable fullnames. This includes builtins,
`collections.abc` collection ABCs, and `typing.Generic`:

```text
builtins.int
builtins.list
collections.abc.Sequence
typing.Generic
```

All other runtime classes are treated as dynamic and receive identity-qualified
fullnames:

```text
{name_hint}@{suffix}
```

The name hint is best-effort human-readable text, normally
`{__module__}.{__qualname__}`. If those attributes are missing or unusable, the
universe falls back to `__name__`, then `type`.

The suffix mode is selected when constructing the universe:

```python
RuntimeTypeUniverse()
RuntimeTypeUniverse(dynamic_type_name_suffix=DYNAMIC_TYPE_NAME_ID)
RuntimeTypeUniverse(dynamic_type_name_suffix='counter')
```

`DYNAMIC_TYPE_NAME_ID` is the default. It appends `id(cls)` as lowercase
hexadecimal:

```text
some.module.User@7fabc123
```

`'counter'` appends a deterministic 1-based counter assigned in
first-seen order within that universe:

```text
some.module.User@1
some.module.Other@2
```

Counter mode is useful for tests and reproducible debug output. It is still
universe-local and not durable serialization.

The runtime universe strongly references runtime classes for now. Weakrefs and
cache eviction remain deliberately out of scope.

Semantic operations continue to rely on `TypeInfo` identity. Dynamic fullnames
are for display, diagnostics, and disambiguation only.
