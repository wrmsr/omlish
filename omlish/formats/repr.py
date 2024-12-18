import ast
import typing as ta

from .codecs import make_object_lazy_loaded_codec
from .codecs import make_str_object_codec


##


def dumps(obj: ta.Any) -> str:
    return repr(obj)


def loads(s: str) -> ta.Any:
    return ast.literal_eval(s)


##


REPR_CODEC = make_str_object_codec('repr', dumps, loads)

# @omlish-manifest
_REPR_LAZY_CODEC = make_object_lazy_loaded_codec(__name__, 'REPR_CODEC', REPR_CODEC)
