# Dynamic Runtime Type Names

The runtime universe currently needs a clearer policy for classes that are not
stable, known type objects. This includes local classes, classes produced by
decorators or metaclasses, reload-created classes, and ordinary application
classes whose module/qualname should not be treated as durable identity.

The planned direction is that known runtime types keep stable names, while all
other runtime classes get identity-qualified names.

Known examples:

```text
builtins.int
builtins.list
collections.abc.Sequence
typing.Generic
```

Dynamic examples:

```text
some.module.User@7fabc123
some.module.User@1
test_mod.make_box.<locals>.Box@2
type@3
```

The part before `@` is a best-effort human-readable name hint, usually
`{__module__}.{__qualname__}`. If those attributes are missing or unusable, the
fallback hint is based on `__name__`, then finally `type`.

The part after `@` is the identity suffix. It is the part that makes the name
unique within a runtime universe.

Two suffix modes are planned:

- `id`: use `id(cls)` formatted as lowercase hexadecimal. This should be the
  normal runtime mode.
- `counter`: use a deterministic 1-based counter assigned when the universe
  first sees each dynamic class. This is intended for tests and reproducible
  debug output.

The counter should be owned by `RuntimeTypeUniverse`, not by string rendering.
Once a `TypeInfo.fullname` is assigned, all downstream display code should just
render that fullname.

The separator should be `@`, not `&`. `&` may eventually collide visually or
syntactically with intersection types if Python exposes them. `@` is not a
valid character in Python module/class qualified names, and it also matches the
existing project convention for attaching object identity in repr-like output.

This policy intentionally punts on weak references and cache eviction. For now,
the universe can strongly reference runtime classes and their `TypeInfo`
objects. That means `id(cls)` reuse is not a concern within a universe lifetime.

This is not durable serialization. Dynamic fullnames are process/universe-local
debug identifiers. Semantic operations should continue to rely on `TypeInfo`
object identity, not on parsing these strings.
