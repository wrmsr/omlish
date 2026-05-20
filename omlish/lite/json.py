import functools
import json
import typing as ta

from .io import FnWriter


JsonStyle = ta.Literal['pretty', 'compact', None]  # ta.TypeAlias


##


JSON_PRETTY_INDENT = 2

JSON_PRETTY_KWARGS: ta.Mapping[str, ta.Any] = dict(
    indent=JSON_PRETTY_INDENT,
)

json_dump_pretty: ta.Callable[..., None] = functools.partial(json.dump, **JSON_PRETTY_KWARGS)
json_dumps_pretty: ta.Callable[..., str] = functools.partial(json.dumps, **JSON_PRETTY_KWARGS)


##


JSON_COMPACT_SEPARATORS = (',', ':')

JSON_COMPACT_KWARGS: ta.Mapping[str, ta.Any] = dict(
    indent=None,
    separators=JSON_COMPACT_SEPARATORS,
)

json_dump_compact: ta.Callable[..., None] = functools.partial(json.dump, **JSON_COMPACT_KWARGS)
json_dumps_compact: ta.Callable[..., str] = functools.partial(json.dumps, **JSON_COMPACT_KWARGS)


##


JSON_KWARGS_BY_STYLE: ta.Mapping[JsonStyle, ta.Mapping[str, ta.Any]] = {
    'pretty': JSON_PRETTY_KWARGS,
    'compact': JSON_COMPACT_KWARGS,
    None: {},
}


##


def json_dump(
        obj: ta.Any,
        fp: ta.Any,
        *,
        style: JsonStyle = None,
        **kwargs: ta.Any,
) -> None:
    json.dump(
        obj,
        fp,
        **JSON_KWARGS_BY_STYLE[style],
        **kwargs,
    )


def json_dump_encode(
        obj: ta.Any,
        fp: ta.Any,
        encoding: str = 'utf-8',
        *,
        errors: str = 'strict',
        style: JsonStyle = None,
        **kwargs: ta.Any,
) -> None:
    def write(s: str) -> int:
        fp.write(s.encode(encoding, errors))
        return len(s)

    json.dump(
        obj,
        FnWriter(write),
        **JSON_KWARGS_BY_STYLE[style],
        **kwargs,
    )


def json_dumps(
        obj: ta.Any,
        *,
        style: JsonStyle = None,
        **kwargs: ta.Any,
) -> str:
    return json.dumps(
        obj,
        **JSON_KWARGS_BY_STYLE[style],
        **kwargs,
    )
