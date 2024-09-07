"""
TODO:
 - backend abstr
 - streaming
"""
import functools
import json as _json
import typing as ta

from .. import lang


if ta.TYPE_CHECKING:
    import orjson as _orjson
    import ujson as _ujson

else:
    _orjson = lang.proxy_import('orjson')
    _ujson = lang.proxy_import('ujson')


##


dump = _json.dump
dumps = _json.dumps

detect_encoding = _json.detect_encoding

load = _json.load
loads = _json.loads


##


PRETTY_INDENT = 2

PRETTY_KWARGS: ta.Mapping[str, ta.Any] = dict(
    indent=PRETTY_INDENT,
)

dump_pretty: ta.Callable[..., bytes] = functools.partial(dump, **PRETTY_KWARGS)  # type: ignore
dumps_pretty: ta.Callable[..., str] = functools.partial(dumps, **PRETTY_KWARGS)


##


COMPACT_SEPARATORS = (',', ':')

COMPACT_KWARGS: ta.Mapping[str, ta.Any] = dict(
    indent=None,
    separators=COMPACT_SEPARATORS,
)

dump_compact: ta.Callable[..., bytes] = functools.partial(dump, **COMPACT_KWARGS)  # type: ignore
dumps_compact: ta.Callable[..., str] = functools.partial(dumps, **COMPACT_KWARGS)
