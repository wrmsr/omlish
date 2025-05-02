import typing as ta

from ..codecs import make_object_lazy_loaded_codec
from ..codecs import make_str_object_codec
from .parsing import parse


##


def dumps(obj: ta.Any) -> str:
    # return json.dumps(obj)
    raise NotImplementedError


def loads(s: str) -> ta.Any:
    return parse(s)


##


EDN_CODEC = make_str_object_codec('edn', dumps, loads)

# @omlish-manifest
_EDN_LAZY_CODEC = make_object_lazy_loaded_codec(__name__, 'EDN_CODEC', EDN_CODEC)
