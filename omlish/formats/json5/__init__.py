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

    from .literals import (  # noqa
        translate_string_literal,
        parse_string_literal,

        parse_number_literal,
    )

    from .rendering import (  # noqa
        Json5Renderer,
    )
