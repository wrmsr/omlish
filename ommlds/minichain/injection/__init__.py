from omlish import lang as _lang


with _lang.auto_proxy_init(globals()):
    ##

    from ..events.injection import (  # noqa
        event_callbacks,
    )
