import dataclasses as dc
import typing as ta

from ... import codecs
from ... import lang
from ..coro import buffer_bytes_stepped_reader_coro
from .base import Compression
from .base import IncrementalCompression


##


@dc.dataclass(frozen=True)
class CompressionEagerCodec(codecs.EagerCodec[lang.Bytes, lang.Bytes]):
    compression: Compression

    def encode(self, i: lang.Bytes) -> lang.Bytes:
        return self.compression.compress(i)

    def decode(self, o: lang.Bytes) -> lang.Bytes:
        return self.compression.decompress(o)


##


@dc.dataclass(frozen=True)
class CompressionIncrementalCodec(codecs.IncrementalCodec[lang.Bytes, lang.Bytes]):
    compression: IncrementalCompression

    def encode_incremental(self) -> ta.Generator[lang.Bytes | None, lang.Bytes]:
        return self.compression.compress_incremental()

    def decode_incremental(self) -> ta.Generator[lang.Bytes | None, lang.Bytes]:
        return buffer_bytes_stepped_reader_coro(self.compression.decompress_incremental())


##


class CompressionCodec(codecs.Codec):
    pass


def make_compression_codec(
        name: str,
        cls: type[Compression],
        *,
        aliases: ta.Sequence[str] | None = None,
) -> CompressionCodec:
    return CompressionCodec(
        name=name,
        aliases=aliases,

        input=lang.Bytes,
        output=lang.Bytes,

        new=lambda *args, **kwargs: CompressionEagerCodec(cls(*args, **kwargs)),

        new_incremental=(
            lambda *args, **kwargs: CompressionIncrementalCodec(cls(*args, **kwargs))  # noqa
        ) if issubclass(cls, IncrementalCompression) else None,
    )


##


def make_compression_lazy_loaded_codec(
        module: str,
        attr: str,
        codec: CompressionCodec,
) -> codecs.LazyLoadedCodec:
    return codecs.LazyLoadedCodec.new(
        module,
        attr,
        codec,
    )
