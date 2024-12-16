import typing as ta

from .. import lang
from .codecs import make_bytes_object_codec
from .codecs import make_object_lazy_loaded_codec


if ta.TYPE_CHECKING:
    import cloudpickle
else:
    cloudpickle = lang.proxy_import('cloudpickle')


##


def dump(obj: ta.Any) -> bytes:
    return cloudpickle.dumps(obj)


def load(s: bytes) -> ta.Any:
    return cloudpickle.loads(s)


##


CLOUDPICKLE_CODEC = make_bytes_object_codec('cloudpickle', dump, load)

# @omlish-manifest
_CLOUDPICKLE_LAZY_CODEC = make_object_lazy_loaded_codec(__name__, 'CLOUDPICKLE_CODEC', CLOUDPICKLE_CODEC)
