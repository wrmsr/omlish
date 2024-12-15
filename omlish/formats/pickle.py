import typing as ta

from .. import lang
from .codecs import make_bytes_object_codec
from .codecs import make_object_lazy_loaded_codec


if ta.TYPE_CHECKING:
    import pickle
else:
    pickle = lang.proxy_import('pickle')


##


def dump(obj: ta.Any) -> bytes:
    return pickle.dumps(obj)


def load(s: bytes) -> ta.Any:
    return pickle.loads(s)


##


PICKLE_CODEC = make_bytes_object_codec('pickle', dump, load)

# @omlish-manifest
_PICKLE_LAZY_CODEC = make_object_lazy_loaded_codec(__name__, 'PICKLE_CODEC', PICKLE_CODEC)
