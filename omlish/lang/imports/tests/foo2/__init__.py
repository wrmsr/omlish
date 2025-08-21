from ...proxyinit import auto_proxy_init


with auto_proxy_init(globals()):
    import math  # noqa

    from . import qux  # noqa

    from .bar.baz import (  # noqa
        abc,
        ghi,
    )

    import math as math2  # noqa

    from . import qux as qux2  # noqa

    from .bar.baz import jkl as jkl2  # noqa
