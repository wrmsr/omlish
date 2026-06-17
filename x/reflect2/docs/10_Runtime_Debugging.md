# Runtime Debugging Helpers

This step added a small debug/display layer around the type IR.

The core entry point is `type_str()`, which accepts an already-reflected
`Type` node and renders a readable representation. This belongs to the core IR
side because it does not inspect Python runtime typing objects. It is intended
for diagnostics, tests, assertions, and interactive development.

The runtime convenience wrappers live in `runtime/ops.py`:

- `reflect_type_str(obj)` reflects a runtime typing object and then calls
  `type_str()`.
- `reflect_type_strs(objs)` does the same for a sequence of runtime objects.

Examples of current display output:

```python
reflect_type_str(list[int])
# builtins.list[builtins.int]

reflect_type_str(int | None)
# Union[builtins.int, None]

reflect_type_strs([int, str])
# ['builtins.int', 'builtins.str']
```

Base-query helpers return IR types, so their results can be rendered with the
core stringifier:

```python
args = reflect_base_args(list[int], collections.abc.Iterable)
display = [type_str(arg) for arg in args]
# ['builtins.int']
```

These strings are deliberately not a serialization format. They should not be
used as durable cache keys, persisted identifiers, or round-trip syntax. The
package still has no source-awareness and no persistent cache surface; this is
only a human-facing debug representation.

Runtime wrappers keep the same fail-closed behavior as the rest of the runtime
reflection API. If a runtime object cannot be reflected, the wrapper propagates
`UnreflectableTypeError` instead of fabricating a partial string. Core code that
already has a `Type` should call `type_str()` directly.
