# ruff: noqa: I001
from .... import lang as _lang


with _lang.auto_proxy_init(globals()):
    ##

    from . import adapters  # noqa

    from . import queries  # noqa
    from . import queries as q  # noqa
