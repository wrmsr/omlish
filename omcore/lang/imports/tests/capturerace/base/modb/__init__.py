import time

from .....proxy import auto_proxy_init


time.sleep(1)

with auto_proxy_init(globals()):
    time.sleep(1)

    from . import suba  # noqa
    from .subb import b  # noqa
