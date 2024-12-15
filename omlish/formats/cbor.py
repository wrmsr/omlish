import typing as ta

from .. import lang
from .codecs import make_bytes_object_codec
from .codecs import make_object_lazy_loaded_codec


if ta.TYPE_CHECKING:
    import cbor2
else:
    cbor2 = lang.proxy_import('cbor2')


##


def dump(obj: ta.Any) -> bytes:
    return cbor2.dumps(obj)


def load(s: bytes) -> ta.Any:
    return cbor2.loads(s)


##


CBOR_CODEC = make_bytes_object_codec('cbor', dump, load)

# @omlish-manifest
_CBOR_LAZY_CODEC = make_object_lazy_loaded_codec(__name__, 'CBOR_CODEC', CBOR_CODEC)
