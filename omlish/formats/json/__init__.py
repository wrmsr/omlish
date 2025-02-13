# ruff: noqa: I001
"""
TODO:
 - delimited.py / jsonl
  - + record separators ala https://en.wikipedia.org/wiki/JSON_streaming
"""
import typing as _ta

from ... import lang as _lang


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

from .json import (  # noqa
    dump,
    dump_compact,
    dump_pretty,
    dumps,
    dumps_compact,
    dumps_pretty,
    load,
    loads,
)

if _ta.TYPE_CHECKING:
    from .render import (  # noqa
        JsonRenderer,
    )
else:
    _lang.proxy_init(globals(), '.render', [
        'JsonRenderer',
    ])

from .types import (  # noqa
    SCALAR_TYPES,
    Scalar,
)
