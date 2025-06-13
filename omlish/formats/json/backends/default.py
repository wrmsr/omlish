import typing as ta

from .... import lang
from .base import Backend
from .orjson import orjson_backend
from .std import std_backend
from .ujson import ujson_backend


##


@lang.cached_function
def default_backend() -> Backend:
    for fn in [
        orjson_backend,
        ujson_backend,
    ]:
        if (be := fn()) is not None:
            return be

    return std_backend()


##


def dump(obj: ta.Any, fp: ta.Any, **kwargs: ta.Any) -> None:
    return default_backend().dump(obj, fp, **kwargs)


def dumps(obj: ta.Any, **kwargs: ta.Any) -> str:
    return default_backend().dumps(obj, **kwargs)


def load(fp: ta.Any, **kwargs: ta.Any) -> ta.Any:
    return default_backend().load(fp, **kwargs)


def loads(s: str | bytes | bytearray, **kwargs: ta.Any) -> ta.Any:
    return default_backend().loads(s, **kwargs)


def dump_pretty(obj: ta.Any, fp: ta.Any, **kwargs: ta.Any) -> None:
    return default_backend().dump_pretty(obj, fp, **kwargs)


def dumps_pretty(obj: ta.Any, **kwargs: ta.Any) -> str:
    return default_backend().dumps_pretty(obj, **kwargs)


def dump_compact(obj: ta.Any, fp: ta.Any, **kwargs: ta.Any) -> None:
    return default_backend().dump_compact(obj, fp, **kwargs)


def dumps_compact(obj: ta.Any, **kwargs: ta.Any) -> str:
    return default_backend().dumps_compact(obj, **kwargs)
