import typing as ta

from .. import lang
from .codecs import make_object_lazy_loaded_codec
from .codecs import make_str_object_codec


if ta.TYPE_CHECKING:
    import json5
else:
    json5 = lang.proxy_import('json5')


##


def dumps(obj: ta.Any) -> str:
    return json5.dumps(obj)


def loads(s: str) -> ta.Any:
    return json5.loads(s)


##


JSON5_CODEC = make_str_object_codec('json5', dumps, loads)

# @omlish-manifest
_JSON5_LAZY_CODEC = make_object_lazy_loaded_codec(__name__, 'JSON5_CODEC', JSON5_CODEC)
