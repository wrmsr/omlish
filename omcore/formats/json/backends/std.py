"""
load(fp: File, **LoadOpts) -> ta.Any | json.JSONDecodeError
loads(s: str | bytes | bytearray, **LoadOpts) -> ta.Any | json.JSONDecodeError
dump(obj: ta.Any, fp: File, **DumpOpts) -> None
dumps(obj: ta.Any, **DumpOpts) -> str
"""
import dataclasses as dc
import json
import typing as ta

from .... import lang
from ..consts import COMPACT_KWARGS
from ..consts import PRETTY_KWARGS
from .base import Backend


##


@dc.dataclass(frozen=True, kw_only=True)
class DumpOpts:
    cls: type[json.JSONEncoder] | None = None
    skipkeys: bool = False  # dict keys that are not basic types will be skipped instead of raising a TypeError
    ensure_ascii: bool = True  # escape non-ASCII characters in JSON strings
    check_circular: bool = True  # if False a circular reference will result in an RecursionError
    allow_nan: bool = True  # use JS equivalents for out-of-range float values, otherwise raise ValueError
    indent: int | None = None  # item indent - 0 will insert only newlines, None is most compact
    separators: tuple[str, str] | None  = None  # (item_separator, key_separator) - default (', ', ': ') if indent is None else (',', ': ')  # noqa
    default: ta.Callable[[ta.Any], ta.Any] | None = None  # should return a serializable version of obj or raise TypeError  # noqa
    sort_keys: bool = False


@dc.dataclass(frozen=True, kw_only=True)
class LoadOpts:
    cls: type[json.JSONDecoder] | None = None

    parse_float: ta.Callable[[str], ta.Any] | None = None  # by default this is equivalent to float(num_str)
    parse_int: ta.Callable[[str], ta.Any] | None = None  # by default this is equivalent to int(num_str)
    parse_constant: ta.Callable[[str], ta.Any] | None = None  # # called with one of the following strings: -Infinity, Infinity, NaN  # noqa

    # called with the result of any object literal decoded
    object_hook: ta.Callable[[dict], ta.Any] | None = None

    # called with the result of any object literal decoded with an ordered list of pairs, by default dict  # noqa
    object_pairs_hook: ta.Callable[[list[tuple[str, ta.Any]]], ta.Any] | None = None


##


class StdBackend(Backend):
    def dump(self, obj: ta.Any, fp: ta.Any, **kwargs: ta.Any) -> None:
        json.dump(obj, fp, **kwargs)

    def dumps(self, obj: ta.Any, **kwargs: ta.Any) -> str:
        return json.dumps(obj, **kwargs)

    def load(self, fp: ta.Any, **kwargs: ta.Any) -> ta.Any:
        return json.load(fp, **kwargs)

    def loads(self, s: str | bytes | bytearray, **kwargs: ta.Any) -> ta.Any:
        return json.loads(s, **kwargs)

    def dump_pretty(self, obj: ta.Any, fp: ta.Any, **kwargs: ta.Any) -> None:
        json.dump(obj, fp, **PRETTY_KWARGS, **kwargs)

    def dumps_pretty(self, obj: ta.Any, **kwargs: ta.Any) -> str:
        return json.dumps(obj, **PRETTY_KWARGS, **kwargs)

    def dump_compact(self, obj: ta.Any, fp: ta.Any, **kwargs: ta.Any) -> None:
        json.dump(obj, fp, **COMPACT_KWARGS, **kwargs)

    def dumps_compact(self, obj: ta.Any, **kwargs: ta.Any) -> str:
        return json.dumps(obj, **COMPACT_KWARGS, **kwargs)


@lang.cached_function
def std_backend() -> StdBackend:
    return StdBackend()
