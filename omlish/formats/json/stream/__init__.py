"""
A generator powered, configurable, mostly fully streaming JSON parser.

Regarding the 'streamyness' of the subsystems:
 - Lexing only buffers for string and number literals.
 - Parsing maintains only a stack that scales by nesting depth.
 - Building values will obviously hold everything under the topmost object it's building until it's finished.

It's reasonably optimized, but performance is not a primary or even secondary goal: its goal is flexibility. If speed
matters use a native library.
"""


from .building import (  # noqa
    JsonValueBuilder,
)

from .errors import (  # noqa
    JsonStreamError,
)


from .lexing import (  # noqa
    IdentTokenKind,
    ValueTokenKind,
    VALUE_TOKEN_KINDS,
    ControlTokenKind,
    SpaceTokenKind,
    TokenKind,

    ScalarValue,
    SCALAR_VALUE_TYPES,

    Position,

    Token,

    CONTROL_TOKENS,
    CONST_IDENT_VALUES,

    JsonStreamLexError,
    JsonStreamLexer,
)

from .parsing import (  # noqa
    BeginObject,
    Key,
    EndObject,
    BeginArray,
    EndArray,

    Event,
    Events,

    yield_parser_events,

    JsonStreamParseError,
    JsonStreamObject,
    JsonStreamParser,
)

from .rendering import (  # noqa
    StreamJsonRenderer,
)

from .utils import (  # noqa
    JsonStreamValueParser,

    stream_parse_values,
    stream_parse_one_value,
    stream_parse_exactly_one_value,
)
