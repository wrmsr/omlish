"""
TOOD:
 - snappy, lz4
"""
import contextlib
import gzip as gzip_
import io
import typing as ta

from .. import defs
from .. import lang
from .registries import EXTENSION_REGISTRY
from .types import Codec


F = ta.TypeVar('F')
T = ta.TypeVar('T')


@EXTENSION_REGISTRY.registering('gz', 'gzip')
class GzipCodec(Codec[F, bytes], lang.Final):

    def __init__(self, compresslevel=9) -> None:
        super().__init__()

        self._compresslevel = compresslevel

    defs.repr()

    def encode(self, o: F) -> bytes:
        buf = io.BytesIO()
        with contextlib.closing(
                gzip_.GzipFile(fileobj=buf, mode='wb', compresslevel=self._compresslevel)) as f:
            f.write(o)
        return buf.getvalue()

    def decode(self, o: bytes) -> F:
        buf = io.BytesIO(o)
        with contextlib.closing(gzip_.GzipFile(fileobj=buf, mode='rb')) as f:
            return f.read()


gzip = GzipCodec


@EXTENSION_REGISTRY.registering('bz2')
class Bz2Codec(Codec[F, bytes], lang.Final):
    _MODULE = lang.lazy_import('bz2')

    def __init__(self, compresslevel=9) -> None:
        super().__init__()

        self._compresslevel = compresslevel

    defs.repr()

    def encode(self, o: F) -> bytes:
        buf = io.BytesIO()
        with contextlib.closing(
                self._MODULE().BZ2File(buf, mode='wb', compresslevel=self._compresslevel)) as f:
            f.write(o)
        return buf.getvalue()

    def decode(self, o: bytes) -> F:
        buf = io.BytesIO(o)
        with contextlib.closing(self._MODULE().BZ2File(buf, mode='rb')) as f:
            return f.read()


bz2 = Bz2Codec


@EXTENSION_REGISTRY.registering('lzma', 'xz')
class LzmaCodec(Codec[F, bytes], lang.Final):
    _MODULE = lang.lazy_import('lzma')

    defs.repr()

    def encode(self, o: F) -> bytes:
        buf = io.BytesIO()
        with contextlib.closing(self._MODULE().LZMAFile(buf, mode='wb')) as f:
            f.write(o)
        return buf.getvalue()

    def decode(self, o: bytes) -> F:
        buf = io.BytesIO(o)
        with contextlib.closing(self._MODULE().LZMAFile(buf, mode='rb')) as f:
            return f.read()


lzma = LzmaCodec


@EXTENSION_REGISTRY.registering('zstd')
class ZstdCodec(Codec[F, bytes], lang.Final):
    _MODULE = lang.lazy_import('zstd')

    defs.repr()

    def encode(self, o: F) -> bytes:
        return self._MODULE().compress(o)

    def decode(self, o: bytes) -> F:
        return self._MODULE().decompress(o)


zstd = ZstdCodec
