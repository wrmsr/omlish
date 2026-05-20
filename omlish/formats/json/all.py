# ruff: noqa: I001
from ... import lang as _lang


with _lang.auto_proxy_init(globals()):
    ##

    from .backends import (  # noqa
        Backend,

        default_backend,

        StdBackend,
        std_backend,
    )

    from .backends.default import (  # noqa
        dump,
        dump_compact,
        dump_pretty,
        dumps,
        dumps_compact,
        dumps_pretty,
        load,
        loads,
    )

    from .consts import (  # noqa
        Separators,

        PRETTY_INDENT,
        PRETTY_KWARGS,
        PRETTY_SEPARATORS,

        COMPACT_KWARGS,
        COMPACT_SEPARATORS,

        KWARGS_BY_STYLE,
    )

    from .encoding import (  # noqa
        decodes,
        detect_encoding,
    )

    from .rendering import (  # noqa
        JsonRenderer,
    )

    from .types import (  # noqa
        SCALAR_TYPES,
        Scalar,
    )

    #

    from ...lite.json import (  # noqa
        JsonStyle as Style,
    )
