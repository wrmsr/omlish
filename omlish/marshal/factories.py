import abc
import dataclasses as dc
import enum
import threading
import typing as ta

from .. import reflect as rfl


R = ta.TypeVar('R')
C = ta.TypeVar('C')
A = ta.TypeVar('A')


##


class Factory(abc.ABC, ta.Generic[R, C, A]):
    @abc.abstractmethod
    def __call__(self, ctx: C, arg: A) -> R | None:
        raise NotImplementedError


##


@dc.dataclass(frozen=True)
class FuncFactory(ta.Generic[R, C, A]):
    fn: ta.Callable[[C, A], R | None]

    def __call__(self, ctx: C, arg: A) -> R | None:
        return self.fn(ctx, arg)


##


@dc.dataclass(frozen=True)
class TypeMapFactory(Factory[R, C, rfl.Type]):
    m: ta.Mapping[rfl.Type, R] = dc.field(default_factory=dict)

    def __call__(self, ctx: C, rty: rfl.Type) -> R | None:
        return self.m.get(rty)


##


class TypeCacheFactory(Factory[R, C, rfl.Type]):
    def __init__(self, f: Factory[R, C, rfl.Type]) -> None:
        super().__init__()
        self._f = f
        self._dct: dict[rfl.Type, R | None] = {}
        self._mtx = threading.RLock()

    def __call__(self, ctx: C, rty: rfl.Type) -> R | None:
        try:
            return self._dct[rty]
        except KeyError:
            pass
        with self._mtx:
            try:
                return self._dct[rty]
            except KeyError:
                ret = self._dct[rty] = self._f(ctx, rty)
                return ret


##


class RecursiveTypeFactory(Factory[R, C, rfl.Type]):
    def __init__(
            self,
            f: Factory[R, C, rfl.Type],
            prx: ta.Callable[[], tuple[R | None, ta.Callable[[R | None], None]]],
    ) -> None:
        super().__init__()
        self._f = f
        self._prx = prx
        self._dct: dict[rfl.Type, R | None] = {}

    def __call__(self, ctx: C, rty: rfl.Type) -> R | None:
        try:
            return self._dct[rty]
        except KeyError:
            pass
        p, sp = self._prx()
        self._dct[rty] = p
        try:
            r = self._f(ctx, rty)
            sp(r)
            return r
        finally:
            del self._dct[rty]


##


class CompositeFactory(Factory[R, C, A]):
    class Strategy(enum.Enum):
        FIRST = enum.auto()
        ONE = enum.auto()

    def __init__(self, *fs: Factory[R, C, A], strategy: Strategy = Strategy.FIRST) -> None:
        super().__init__()
        self._fs = fs
        self._st = strategy

    def __call__(self, ctx: C, arg: A) -> R | None:
        w: list[R] = []
        for c in self._fs:
            if (r := c(ctx, arg)) is None:
                continue
            if self._st is CompositeFactory.Strategy.FIRST:
                return r
            w.append(r)

        if not w:
            return None

        if self._st is CompositeFactory.Strategy.ONE:
            if len(w) == 1:
                return w[0]

            raise TypeError(f'multiple implementations: {arg} {w}')

        raise TypeError(f'unknown composite strategy: {self._st}')
