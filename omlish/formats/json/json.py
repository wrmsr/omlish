"""
TODO:
 - backend abstr
 - streaming
"""
import functools
import json as _json
import typing as ta

from .consts import COMPACT_KWARGS
from .consts import PRETTY_KWARGS


##


dump = _json.dump
dumps = _json.dumps

detect_encoding = _json.detect_encoding

load = _json.load
loads = _json.loads


##


dump_pretty: ta.Callable[..., bytes] = functools.partial(dump, **PRETTY_KWARGS)  # type: ignore
dumps_pretty: ta.Callable[..., str] = functools.partial(dumps, **PRETTY_KWARGS)


##


dump_compact: ta.Callable[..., bytes] = functools.partial(dump, **COMPACT_KWARGS)  # type: ignore
dumps_compact: ta.Callable[..., str] = functools.partial(dumps, **COMPACT_KWARGS)
