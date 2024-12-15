from ...codecs import Codec
from ...codecs import LazyLoadedCodec


BZ2_CODEC = Codec(
    name='bz2',
    input=bytes,
    output=bytes,
    new=lambda: None,
)

# @omlish-manifest
_BZ2_LAZY_CODEC = LazyLoadedCodec.new(__name__, 'BZ2_CODEC', BZ2_CODEC)
