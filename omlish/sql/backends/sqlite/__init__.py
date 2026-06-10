# ruff: noqa: I001
from .... import lang as _lang


with _lang.auto_proxy_init(globals()):
    ##

    from . import backend  # noqa

    from . import dialect  # noqa

    from . import inspect  # noqa

    from . import tabledefs  # noqa
    from . import tabledefs as td  # noqa
