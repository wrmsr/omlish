import dataclasses as dc
import typing as ta

from ... import codecs
from ..generators import buffer_bytes_stepped_reader_generator
from .base import Compression
from .base import IncrementalCompression


##


@dc.dataclass(frozen=True)
class CompressionEagerCodec(codecs.EagerCodec[bytes, bytes]):
    compression: Compression

    def encode(self, i: bytes) -> bytes:
        return self.compression.compress(i)

    def decode(self, o: bytes) -> bytes:
        return self.compression.decompress(o)


##


@dc.dataclass(frozen=True)
class CompressionIncrementalCodec(codecs.IncrementalCodec[bytes, bytes]):
    compression: IncrementalCompression

    def encode_incremental(self) -> ta.Generator[bytes | None, bytes, None]:
        return self.compression.compress_incremental()

    def decode_incremental(self) -> ta.Generator[bytes | None, bytes, None]:
        return buffer_bytes_stepped_reader_generator(self.compression.decompress_incremental())


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

        new_incremental=(
            lambda *args, **kwargs: CompressionIncrementalCodec(cls(*args, **kwargs))  # noqa
        ) if issubclass(cls, IncrementalCompression) else None,
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
