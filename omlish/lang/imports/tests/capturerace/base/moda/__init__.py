from .....proxy import auto_proxy_init


with auto_proxy_init(globals()):
    from . import suba
    from .subb import b
