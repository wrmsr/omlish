import typing as ta

from .errors import Json5Error
from .stream import stream_parse_exactly_one_value
from .stream import stream_parse_values


##


def parse(buf: str) -> ta.Any:
    try:
        return stream_parse_exactly_one_value(buf)

    except Exception as e:  # noqa
        # FIXME: lol
        raise Json5Error from e


def parse_many(buf: str) -> ta.Iterator[ta.Any]:
    try:
        return stream_parse_values(buf)

    except Exception as e:  # noqa
        # FIXME: lol
        raise Json5Error from e
