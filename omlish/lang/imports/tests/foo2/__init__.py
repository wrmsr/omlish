from ...proxyinit import auto_proxy_init


with auto_proxy_init(globals()):
    import math  # noqa

    from . import qux  # noqa

    from .bar.baz import (  # noqa
        abc,
        ghi,
    )
