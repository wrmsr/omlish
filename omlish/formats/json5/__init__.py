from ... import lang as _lang


with _lang.auto_proxy_init(globals()):
    ##

    from .codec import (  # noqa
        dump,
        dump_compact,
        dump_pretty,
        dumps,
        dumps_pretty,
        dumps_compact,
        load,
        loads,
    )

    from .errors import (  # noqa
        Json5Error,
    )
