# ruff: noqa: I001
"""
TODO:
 - delimited.py / jsonl
  - + record separators ala https://en.wikipedia.org/wiki/JSON_streaming
"""
import typing as _ta

from ... import lang as _lang


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

if _ta.TYPE_CHECKING:
    from .rendering import (  # noqa
        JsonRenderer,
    )
else:
    _lang.proxy_init(globals(), '.rendering', [
        'JsonRenderer',
    ])

from .types import (  # noqa
    SCALAR_TYPES,
    Scalar,
)
