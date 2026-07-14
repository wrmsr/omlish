import typing as ta

from ..json.stream.errors import JsonStreamError
from ..json.stream.utils import DebugJsonStreamValueParser
from ..json.stream.utils import JsonStreamValueParser
from .errors import Json5Error
from .stream import make_machinery


##


def parse(
        buf: str,
        *,
        debug: bool = False,
        **kwargs: ta.Any,
) -> ta.Any:
    m = make_machinery(**kwargs)

    if debug:
        vc: type[JsonStreamValueParser] = DebugJsonStreamValueParser
    else:
        vc = JsonStreamValueParser

    try:
        return vc.parse_exactly_one_value(m, buf)

    except Json5Error:
        raise

    except JsonStreamError as e:
        raise Json5Error from e


def parse_many(
        buf: str,
        *,
        debug: bool = False,
        **kwargs: ta.Any,
) -> ta.Iterator[ta.Any]:
    m = make_machinery(**kwargs)

    if debug:
        vc: type[JsonStreamValueParser] = DebugJsonStreamValueParser
    else:
        vc = JsonStreamValueParser

    try:
        yield from vc.parse_values(m, buf)

    except Json5Error:
        raise

    except JsonStreamError as e:
        raise Json5Error from e
