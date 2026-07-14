import time

from .....proxy import auto_proxy_init


with auto_proxy_init(globals()):
    time.sleep(2)

    from . import suba  # noqa
    from .subb import b  # noqa
