"""A fixture module which sets a foreign attribute on a captured module - importing it must raise an AttrError."""
from ..proxy import auto_proxy_import


with auto_proxy_import(globals()):
    import json

    json.foo = 1  # type: ignore[attr-defined]
