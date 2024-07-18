import abc
import codecs
import dataclasses as dc
import typing as ta


T = ta.TypeVar('T')
F = ta.TypeVar('F')


class FnPair(ta.Generic[F, T], abc.ABC):
    @abc.abstractmethod
    def forward(self, f: F) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def backward(self, t: T) -> F:
        raise NotImplementedError


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


invert = Inverted


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


compose = Composite


##


@dc.dataclass(frozen=True)
class Text(FnPair[str, bytes]):
    ci: codecs.CodecInfo
    encode_errors: str = dc.field(default='strict', kw_only=True)
    decode_errors: str = dc.field(default='strict', kw_only=True)

    def forward(self, f: str) -> bytes:
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
