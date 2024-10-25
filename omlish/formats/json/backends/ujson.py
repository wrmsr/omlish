"""
load(fp: File) -> ta.Any | uj.JSONDecodeError
loads(s: str | bytes | bytearray) -> ta.Any | uj.JSONDecodeError
dump(obj: ta.Any, fp: File, **DumpOpts) -> None
dumps(obj: ta.Any, **DumpOpts) -> None
"""
import dataclasses as dc
import typing as ta

from .... import lang
from ..consts import PRETTY_INDENT
from .base import Backend


if ta.TYPE_CHECKING:
    import ujson as uj
else:
    uj = lang.proxy_import('ujson')


##


@dc.dataclass(frozen=True, kw_only=True)
class DumpOpts:
    """
    https://github.com/ultrajson/ultrajson/blob/2e4aba339b0ab08f893590aaa989d12846afc5d6/python/objToJSON.c#L662
    """

    ensure_ascii: bool = True  # limits output to ASCII and escapes all extended characters above 127.
    encode_html_chars: bool = False  # enables special encoding of "unsafe" HTML characters into safer Unicode sequences
    escape_forward_slashes: bool = True  # whether forward slashes (/) are escaped
    indent: int = 0
    sort_keys: bool = False
    allow_nan: bool = True
    reject_bytes: bool = True
    default: ta.Callable[[ta.Any], ta.Any] | None = None  # should return a serializable version of obj or raise TypeError  # noqa
    separators: tuple[str, str] | None = None


##


class UjsonBackend(Backend):
    def dump(self, obj: ta.Any, fp: ta.Any, **kwargs: ta.Any) -> None:
        uj.dump(obj, fp, **kwargs)

    def dumps(self, obj: ta.Any, **kwargs: ta.Any) -> str:
        return uj.dumps(obj, **kwargs)

    def load(self, fp: ta.Any, **kwargs: ta.Any) -> ta.Any:
        return uj.load(fp, **kwargs)

    def loads(self, s: str | bytes | bytearray, **kwargs: ta.Any) -> ta.Any:
        return uj.loads(s, **kwargs)

    def dump_pretty(self, obj: ta.Any, fp: ta.Any, **kwargs: ta.Any) -> None:
        uj.dump(obj, fp, indent=PRETTY_INDENT, **kwargs)

    def dumps_pretty(self, obj: ta.Any, **kwargs: ta.Any) -> str:
        return uj.dumps(obj, indent=PRETTY_INDENT, **kwargs)

    def dump_compact(self, obj: ta.Any, fp: ta.Any, **kwargs: ta.Any) -> None:
        uj.dump(obj, fp, **kwargs)

    def dumps_compact(self, obj: ta.Any, **kwargs: ta.Any) -> str:
        return uj.dumps(obj, **kwargs)


UJSON_BACKEND: UjsonBackend | None
if lang.can_import('ujson'):
    UJSON_BACKEND = UjsonBackend()
else:
    UJSON_BACKEND = None
