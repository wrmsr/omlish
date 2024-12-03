"""
TODO:
 - ** move into ../serde ? **
 - msgpack
  - https://github.com/vsergeev/u-msgpack-python ?
 - cloudpickle
 - https://github.com/agronholm/cbor2 ?
"""
import io
import pickle as pickle_
import struct as struct_
import typing as ta

from .. import defs
from .. import lang
from .registries import EXTENSION_REGISTRY
from .registries import MIME_TYPE_REGISTRY
from .types import Codec


F = ta.TypeVar('F')
T = ta.TypeVar('T')


class StructCodec(Codec[F, bytes], lang.Final):

    def __init__(self, fmt: str) -> None:
        super().__init__()

        self._fmt = fmt

    defs.repr()

    def encode(self, o: F) -> bytes:
        return struct_.pack(self._fmt, *o)

    def decode(self, o: bytes) -> F:
        return struct_.unpack(self._fmt, o)


struct = StructCodec


@EXTENSION_REGISTRY.registering('pickle')
@MIME_TYPE_REGISTRY.registering('application/python-pickle')
class PickleCodec(Codec[F, bytes], lang.Final):

    def __init__(self, protocol=None, *, fix_imports=True) -> None:
        super().__init__()

        self._protocol = protocol
        self._fix_imports = fix_imports

    defs.repr()

    def encode(self, o: F) -> bytes:
        return pickle_.dumps(o, self._protocol, fix_imports=self._fix_imports)

    def decode(self, o: bytes) -> F:
        return pickle_.loads(o)


pickle = PickleCodec


@EXTENSION_REGISTRY.registering('yaml', 'yml')
@MIME_TYPE_REGISTRY.registering(
    'application/x-yaml',
    'text/x-yaml',
    'text/yaml',
)
class YamlCodec(Codec[F, str], lang.Final):
    _MODULE = lang.lazy_import('yaml')

    defs.repr()

    def encode(self, o: F) -> str:
        return self._MODULE().dump(o)

    def decode(self, o: str) -> F:
        mod = self._MODULE()
        return mod.load(o, Loader=mod.FullLoader)


yaml = YamlCodec


@EXTENSION_REGISTRY.registering('bson')
@MIME_TYPE_REGISTRY.registering('application/bson')
class BsonCodec(Codec[F, bytes], lang.Final):
    _MODULE = lang.lazy_import('bson')

    defs.repr()

    @lang.cached_nullary  # noqa
    @classmethod
    def _fns(cls):
        mod = cls._MODULE()
        for ea, da in (
                ('dumps', 'loads'),    # bson
                ('encode', 'decode'),  # pymongo's bson
        ):
            if all(hasattr(mod, a) for a in (ea, da)):
                efn = getattr(mod, ea)
                dfn = getattr(mod, da)
                return efn, dfn
        raise RuntimeError('Cannot figure out bson dep')

    def encode(self, o: F) -> bytes:
        return self._fns()[0](o)

    def decode(self, o: bytes) -> F:
        return self._fns()[1](o)


bson = BsonCodec


@EXTENSION_REGISTRY.registering('cbor')
@MIME_TYPE_REGISTRY.registering('application/cbor')
class CborCodec(Codec[F, bytes], lang.Final):
    _MODULE = lang.lazy_import('cbor')

    defs.repr()

    def encode(self, o: F) -> bytes:
        buf = io.BytesIO()
        self._MODULE().dump(o, buf)
        buf.seek(0)
        return buf.read()

    def decode(self, o: bytes) -> F:
        return self._MODULE().load(io.BytesIO(o))


cbor = CborCodec


@EXTENSION_REGISTRY.registering('toml')
@MIME_TYPE_REGISTRY.registering('application/toml')
class TomlCodec(Codec[F, str], lang.Final):
    _MODULE = lang.lazy_import('toml')

    defs.repr()

    def encode(self, o: F) -> str:
        return self._MODULE().dumps(o)

    def decode(self, o: str) -> F:
        return self._MODULE().loads(o)


toml = TomlCodec
