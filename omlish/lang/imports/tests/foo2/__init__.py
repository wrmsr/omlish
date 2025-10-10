from ...proxy import auto_proxy_init, auto_proxy_import  # noqa
import importlib  # noqa


with auto_proxy_init(
        globals(),
        # disable=True,
        unreferenced_callback=lambda u: globals().__setitem__('_auto_proxy_init_unreferenced', u),
) as _cap:  # noqa
    import math  # noqa

    from . import qux  # noqa

    from .bar.baz import (  # noqa
        abc,
        ghi,
        delete_me,
    )

    from collections import Counter  # noqa

    import math as math2  # noqa

    from . import qux as qux2  # noqa

    from .bar.baz import jkl as jkl2  # noqa

    delete_me = None  # type: ignore  # noqa

    jarf2 = qux.jarf  # noqa
    karf = qux.karf  # noqa

    pi = math.pi

    from .deep1.deep2.deep3 import is_deep3  # noqa
    from .deep1.deep4.deep5 import is_deep5  # noqa

    from omlish.lang.imports.tests.foo2.deep1a.deep2a.deep3a import is_deep3a  # noqa
    from omlish.lang.imports.tests.foo2.deep1a.deep4a.deep5a import is_deep5a  # noqa

    import omlish.lang.imports.tests.foo2.deep1b.deep2b.deep3b  # noqa
    import omlish.lang.imports.tests.foo2.deep1b.deep4b.deep5b as my_deep5b  # noqa

    from ..foo3.sub1 import is_foo3_sub1  # noqa
    from ..foo3 import sub2  # noqa
