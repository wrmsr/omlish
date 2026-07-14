"""
This package (together with related `api` modules in sibling packages like `objects`) is the lightweight api intended
to be imported for marshal customization at user definitions. As such it must avoid heavy imports, even if those imports
would otherwise result in faster execution. Notably:

- Use stdlib `dataclasses` not `omlish.dataclasses`
- Use dumb objects for config, not `omlish.typedvalues`
"""
