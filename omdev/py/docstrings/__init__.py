"""Parse docstrings as per Sphinx notation."""
# https://github.com/rr-/docstring_parser/tree/4951137875e79b438d52a18ac971ec0c28ef269c

from .common import (  # noqa
    Docstring,
    DocstringDeprecated,
    DocstringMeta,
    DocstringParam,
    DocstringRaises,
    DocstringReturns,
    DocstringStyle,
    ParseError,
    RenderingStyle,
)

from .parser import (  # noqa
    parse,
    parse_from_object,
)
