"""A fixture module exercising auto_proxy_import's eager mode."""
from ..proxy import auto_proxy_import


with auto_proxy_import(globals(), eager=True):
    import colorsys  # noqa
