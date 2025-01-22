import typing as ta

from .. import json
from ..codecs import make_object_lazy_loaded_codec
from ..codecs import make_str_object_codec
from .parsing import parse


##


def dumps(obj: ta.Any) -> str:
    return json.dumps(obj)


def loads(s: str) -> ta.Any:
    return parse(s)


##


JSON5_CODEC = make_str_object_codec('json5', dumps, loads)

# @omlish-manifest
_JSON5_LAZY_CODEC = make_object_lazy_loaded_codec(__name__, 'JSON5_CODEC', JSON5_CODEC)
