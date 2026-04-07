# ruff: noqa: I001
"""
TODO:
 - delimited.py / jsonl
  - + record separators ala https://en.wikipedia.org/wiki/JSON_streaming
"""
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
        COMPACT_KWARGS,
        COMPACT_SEPARATORS,
        PRETTY_INDENT,
        PRETTY_KWARGS,
        PRETTY_SEPARATORS,
        Separators,
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
