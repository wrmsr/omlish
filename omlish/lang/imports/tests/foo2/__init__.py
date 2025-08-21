from ...proxyinit import auto_proxy_init


with auto_proxy_init(
        globals(),
        unreferenced_callback=lambda u: globals().__setitem__('_auto_proxy_init_unreferenced', u),
):
    import math  # noqa

    from . import qux  # noqa

    from .bar.baz import (  # noqa
        abc,
        ghi,
        delete_me,
    )

    import math as math2  # noqa

    from . import qux as qux2  # noqa

    from .bar.baz import jkl as jkl2  # noqa

    delete_me = None  # type: ignore  # noqa

    jarf2 = qux.jarf  # noqa
    karf = qux.karf  # noqa

    pi = math.pi
