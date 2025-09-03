import abc
import typing as ta

from .. import lang


if ta.TYPE_CHECKING:
    import struct as _struct
else:
    _struct = lang.proxy_import('struct')


##


F = ta.TypeVar('F')
T = ta.TypeVar('T')
U = ta.TypeVar('U')


class FnPair(lang.Abstract, ta.Generic[F, T]):
    @abc.abstractmethod
    def forward(self, f: F) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def backward(self, t: T) -> F:
        raise NotImplementedError

    ##

    def __call__(self, f: F) -> T:
        return self.forward(f)

    def invert(self) -> 'FnPair[T, F]':
        if isinstance(self, Inverted):
            return self._fp
        return Inverted(self)

    def compose(self, nxt: 'FnPair[T, U]') -> 'FnPair[F, U]':
        return Composite((self, nxt))


##


class Simple(FnPair[F, T]):
    def __init__(
            self,
            forward: ta.Callable[[F], T],
            backward: ta.Callable[[T], F],
    ) -> None:
        super().__init__()

        self._forward = self.forward = forward  # type: ignore
        self._backward = self.backward = backward  # type: ignore

    def forward(self, f: F) -> T:
        return self._forward(f)

    def backward(self, t: T) -> F:
        return self._backward(t)


of = Simple

NOP: FnPair[ta.Any, ta.Any] = of(lang.identity, lang.identity)


##


class Inverted(FnPair[F, T]):
    def __init__(self, fp: FnPair[T, F]) -> None:
        super().__init__()

        self._fp = fp

    def forward(self, f: F) -> T:
        return self._fp.backward(f)

    def backward(self, t: T) -> F:
        return self._fp.forward(t)


##


class Composite(FnPair[F, T]):
    def __init__(self, children: ta.Sequence[FnPair]) -> None:
        super().__init__()

        self._children = children

    def forward(self, f: F) -> T:
        for c in self._children:
            f = c.forward(f)
        return ta.cast(T, f)

    def backward(self, t: T) -> F:
        for c in reversed(self._children):
            t = c.backward(t)
        return ta.cast(F, t)


I0 = ta.TypeVar('I0')
I1 = ta.TypeVar('I1')
I2 = ta.TypeVar('I2')
I3 = ta.TypeVar('I3')
I4 = ta.TypeVar('I4')


@ta.overload
def compose(
        fp0: FnPair[F, I0],
        f01: FnPair[I0, T],
) -> FnPair[F, T]:
    ...


@ta.overload
def compose(
        fp0: FnPair[F, I0],
        f01: FnPair[I0, I1],
        fp2: FnPair[I1, T],
) -> FnPair[F, T]:
    ...


@ta.overload
def compose(
        fp0: FnPair[F, I0],
        f01: FnPair[I0, I1],
        fp2: FnPair[I1, I2],
        fp3: FnPair[I2, T],
) -> FnPair[F, T]:
    ...


@ta.overload
def compose(
        fp0: FnPair[F, I0],
        f01: FnPair[I0, I1],
        fp2: FnPair[I1, I2],
        fp3: FnPair[I2, I3],
        fp4: FnPair[I3, T],
) -> FnPair[F, T]:
    ...


@ta.overload
def compose(
        fp0: FnPair[F, I0],
        f01: FnPair[I0, I1],
        fp2: FnPair[I1, I2],
        fp3: FnPair[I2, I3],
        fp4: FnPair[I3, I4],
        fp5: FnPair[I4, T],
) -> FnPair[F, T]:
    ...


@ta.overload
def compose(*ps: FnPair) -> FnPair:
    ...


def compose(*ps):
    if not ps:
        return NOP
    if len(ps) == 1:
        return ps[0]
    return Composite(ps)


##


class Optional(FnPair[F | None, T | None]):
    def __init__(self, fp: FnPair[F, T]) -> None:
        super().__init__()

        self._fp = fp

    def forward(self, f: F | None) -> T | None:
        return None if f is None else self._fp.forward(f)

    def backward(self, t: T | None) -> F | None:
        return None if t is None else self._fp.backward(t)


class Lines(FnPair[ta.Sequence[str], str]):
    def forward(self, f: ta.Sequence[str]) -> str:
        return '\n'.join(f)

    def backward(self, t: str) -> ta.Sequence[str]:
        return t.splitlines()


##


class Struct(FnPair[tuple, bytes]):
    def __init__(self, fmt: str) -> None:
        super().__init__()

        self._fmt = fmt

    def forward(self, f: tuple) -> bytes:
        return _struct.pack(self._fmt, *f)

    def backward(self, t: bytes) -> tuple:
        return _struct.unpack(self._fmt, t)


##


Object: ta.TypeAlias = FnPair[ta.Any, T]
ObjectStr: ta.TypeAlias = Object[str]
ObjectBytes: ta.TypeAlias = Object[bytes]


class Object_(FnPair[ta.Any, T], lang.Abstract):  # noqa
    pass


class ObjectStr_(Object_[str], lang.Abstract):  # noqa
    pass


class ObjectBytes_(Object_[bytes], lang.Abstract):  # noqa
    pass
