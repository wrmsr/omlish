import abc
import codecs
import dataclasses as dc
import typing as ta

from . import lang

if ta.TYPE_CHECKING:
    import bzip2 as _bzip2
    import gzip as _gzip
    import json as _json
    import lzma as _lzma
    import pickle as _pickle
    import struct as _struct
    import tomllib as _tomllib

else:
    _bzip2 = lang.proxy_import('bzip2')
    _gzip = lang.proxy_import('gzip')
    _json = lang.proxy_import('json')
    _lzma = lang.proxy_import('lzma')
    _pickle = lang.proxy_import('pickle')
    _struct = lang.proxy_import('struct')
    _tomllib = lang.proxy_import('tomllib')

_zstd = lang.proxy_import('zstd')
_yaml = lang.proxy_import('yaml')


##


F = ta.TypeVar('F')
T = ta.TypeVar('T')
U = ta.TypeVar('U')


class FnPair(ta.Generic[F, T], abc.ABC):
    @abc.abstractmethod
    def forward(self, f: F) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def backward(self, t: T) -> F:
        raise NotImplementedError

    def invert(self) -> 'FnPair[T, F]':
        if isinstance(self, Inverted):
            return self.fp
        return Inverted(self)

    def compose(self, nxt: 'FnPair[T, U]') -> 'FnPair[F, U]':
        return Composite((self, nxt))


##


@dc.dataclass(frozen=True)
class Simple(FnPair[F, T]):
    forward: ta.Callable[[F], T]  # type: ignore
    backward: ta.Callable[[T], F]  # type: ignore

    def _forward(self, f: F) -> T:
        return self.forward(f)

    def _backward(self, t: T) -> F:
        return self.backward(t)


# HACK: ABC workaround. Our dataclasses handle this with `override=True` but we don't want to dep that in here.
Simple.forward = Simple._forward  # type: ignore  # noqa
Simple.backward = Simple._backward  # type: ignore  # noqa
Simple.__abstractmethods__ = frozenset()  # noqa


of = Simple


##


@dc.dataclass(frozen=True)
class Inverted(FnPair[F, T]):
    fp: FnPair[T, F]

    def forward(self, f: F) -> T:
        return self.fp.backward(f)

    def backward(self, t: T) -> F:
        return self.fp.forward(t)


##


@dc.dataclass(frozen=True)
class Composite(FnPair[F, T]):
    children: ta.Sequence[FnPair]

    def forward(self, f: F) -> T:
        for c in self.children:
            f = c.forward(f)
        return ta.cast(T, f)

    def backward(self, t: T) -> F:
        for c in reversed(self.children):
            t = c.backward(t)
        return ta.cast(F, t)


##


@dc.dataclass(frozen=True)
class Text(FnPair[str, bytes]):
    ci: codecs.CodecInfo
    encode_errors: str = dc.field(default='strict', kw_only=True)
    decode_errors: str = dc.field(default='strict', kw_only=True)

    def forward(self, f: str) -> bytes:
        # Python ignores the returned length:
        #   https://github.com/python/cpython/blob/7431c3799efbd06ed03ee70b64420f45e83b3667/Python/codecs.c#L424
        t, _ = self.ci.encode(f, self.encode_errors)
        return t

    def backward(self, t: bytes) -> str:
        f, _ = self.ci.decode(t, self.decode_errors)
        return f


def text(name: str, *, encode_errors: str = 'strict', decode_errors: str = 'strict') -> Text:
    ci = codecs.lookup(name)
    if not ci._is_text_encoding:  # noqa
        raise TypeError(f'must be text codec: {name}')
    return Text(ci, encode_errors=encode_errors, decode_errors=decode_errors)


UTF8 = text('utf-8')


#


@dc.dataclass(frozen=True)
class Optional(FnPair[ta.Optional[F], ta.Optional[T]]):
    fp: FnPair[F, T]

    def forward(self, f: ta.Optional[F]) -> ta.Optional[T]:
        return None if f is None else self.fp.forward(f)

    def backward(self, t: ta.Optional[T]) -> ta.Optional[F]:
        return None if t is None else self.fp.backward(t)


class Lines(FnPair[ta.Sequence[str], str]):
    def forward(self, f: ta.Sequence[str]) -> str:
        return '\n'.join(f)

    def backward(self, t: str) -> ta.Sequence[str]:
        return t.splitlines()


##


_EXTENSION_REGISTRY: dict[str, type[FnPair]] = {}


def _register_extension(*ss):
    def inner(cls):
        for s in ss:
            if s in _EXTENSION_REGISTRY:
                raise Exception(s)
            _EXTENSION_REGISTRY[s] = cls
        return cls
    return inner


##


class Compression(FnPair[bytes, bytes], abc.ABC):
    pass


@_register_extension('gz')
@dc.dataclass(frozen=True)
class Gzip(Compression):
    compresslevel: int = 9

    def forward(self, f: bytes) -> bytes:
        return _gzip.compress(f, compresslevel=self.compresslevel)

    def backward(self, t: bytes) -> bytes:
        return _gzip.decompress(t)


@_register_extension('bz2')
@dc.dataclass(frozen=True)
class Bzip2(Compression):
    compresslevel: int = 9

    def forward(self, f: bytes) -> bytes:
        return _bzip2.compress(f, compresslevel=self.compresslevel)

    def backward(self, t: bytes) -> bytes:
        return _bzip2.decompress(t)


@_register_extension('lzma')
class Lzma(Compression):
    def forward(self, f: bytes) -> bytes:
        return _lzma.compress(f)

    def backward(self, t: bytes) -> bytes:
        return _lzma.decompress(t)


#


@_register_extension('zstd')
class Zstd(Compression):
    def forward(self, f: bytes) -> bytes:
        return _zstd.compress(f)

    def backward(self, t: bytes) -> bytes:
        return _zstd.decompress(t)


##


@dc.dataclass(frozen=True)
class Struct(FnPair[tuple, bytes]):
    fmt: str

    def forward(self, f: tuple) -> bytes:
        return _struct.pack(self.fmt, *f)

    def backward(self, t: bytes) -> tuple:
        return _struct.unpack(self.fmt, t)


@_register_extension('pkl')
@dc.dataclass(frozen=True)
class Pickle(FnPair[ta.Any, bytes]):
    protocol: int | None = None

    def forward(self, f: ta.Any) -> bytes:
        return _pickle.dumps(f, protocol=self.protocol)

    def backward(self, t: bytes) -> ta.Any:
        return _pickle.loads(t)


@_register_extension('json')
@dc.dataclass(frozen=True)
class Json(FnPair[ta.Any, str]):
    indent: int | str | None = dc.field(default=None, kw_only=True)
    separators: tuple[str, str] | None = dc.field(default=None, kw_only=True)

    def forward(self, f: ta.Any) -> str:
        return _json.dumps(f, indent=self.indent, separators=self.separators)

    def backward(self, t: str) -> ta.Any:
        return _json.loads(t)


JSON = Json()
PRETTY_JSON = Json(indent=2)
COMPACT_JSON = Json(separators=(',', ':'))


@_register_extension('jsonl')
class JsonLines(FnPair[ta.Sequence[ta.Any], str]):
    def forward(self, f: ta.Sequence[ta.Any]) -> str:
        return '\n'.join(_json.dumps(e) for e in f)

    def backward(self, t: str) -> ta.Sequence[ta.Any]:
        return [_json.loads(l) for l in t.splitlines()]


@_register_extension('toml')
class Toml(FnPair[ta.Any, str]):
    def forward(self, f: ta.Any) -> str:
        raise NotImplementedError

    def backward(self, t: str) -> ta.Any:
        return _tomllib.loads(t)


#


@_register_extension('yml', 'yaml')
class Yaml(FnPair[ta.Any, str]):
    def forward(self, f: ta.Any) -> str:
        return _yaml.dump(f)

    def backward(self, t: str) -> ta.Any:
        return _yaml.safe_load(t)


class UnsafeYaml(FnPair[ta.Any, str]):
    def forward(self, f: ta.Any) -> str:
        return _yaml.dump(f)

    def backward(self, t: str) -> ta.Any:
        return _yaml.safe_load(t, loader=_yaml.FullLoader)
