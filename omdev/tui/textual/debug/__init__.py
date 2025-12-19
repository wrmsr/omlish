# ruff: noqa: F401
# flake8: noqa: F401
from omlish import lang as _lang


with _lang.auto_proxy_init(globals()):
    ##

    from . import dominfo  # noqa
    from . import screen  # noqa
