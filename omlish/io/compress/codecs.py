import typing as ta

from ... import codecs
from .base import Compression


##


class CompressionEagerCodec(codecs.EagerCodec[bytes, bytes]):
    def __init__(self, compression: Compression) -> None:
        super().__init__()

        self._compression = compression

    def encode(self, i: bytes) -> bytes:
        return self._compression.compress(i)

    def decode(self, o: bytes) -> bytes:
        return self._compression.decompress(o)


##


class CompressionCodec(codecs.Codec):
    pass


def make_compression_codec(
        name: str,
        cls: type[Compression],
        *,
        aliases: ta.Collection[str] | None = None,
) -> CompressionCodec:
    return CompressionCodec(
        name=name,
        aliases=aliases,

        input=bytes,
        output=bytes,

        new=lambda *args, **kwargs: CompressionEagerCodec(cls(*args, **kwargs)),
    )


##


def make_compression_lazy_loaded_codec(
        mod_name: str,
        attr_name: str,
        codec: CompressionCodec,
) -> codecs.LazyLoadedCodec:
    return codecs.LazyLoadedCodec.new(
        mod_name,
        attr_name,
        codec,
    )
