import abc
import dataclasses as dc
import enum
import threading
import typing as ta

from .specs import Spec


R = ta.TypeVar('R')
C = ta.TypeVar('C')
A = ta.TypeVar('A')


##


class Factory(abc.ABC, ta.Generic[R, C, A]):
    @abc.abstractmethod
    def __call__(self, ctx: C, arg: A) -> ta.Optional[R]:
        raise NotImplementedError


##


@dc.dataclass(frozen=True)
class FuncFactory(ta.Generic[R, C, A]):
    fn: ta.Callable[[C, A], ta.Optional[R]]

    def __call__(self, ctx: C, arg: A) -> ta.Optional[R]:
        return self.fn(ctx, arg)


##


@dc.dataclass(frozen=True)
class SpecMapFactory(Factory[R, C, Spec]):
    m: ta.Mapping[Spec, R] = dc.field(default_factory=dict)

    def __call__(self, ctx: C, spec: Spec) -> ta.Optional[R]:
        return self.m.get(spec)


##


class SpecCacheFactory(Factory[R, C, Spec]):
    def __init__(self, f: Factory[R, C, Spec]) -> None:
        super().__init__()
        self._f = f
        self._dct: dict[Spec, ta.Optional[R]] = {}
        self._mtx = threading.RLock()

    def __call__(self, ctx: C, spec: Spec) -> ta.Optional[R]:
        try:
            return self._dct[spec]
        except KeyError:
            pass
        with self._mtx:
            try:
                return self._dct[spec]
            except KeyError:
                ret = self._dct[spec] = self._f(ctx, spec)
                return ret


##


class RecursiveSpecFactory(Factory[R, C, Spec]):
    def __init__(
            self,
            f: Factory[R, C, Spec],
            prx: ta.Callable[[], ta.Tuple[ta.Optional[R], ta.Callable[[ta.Optional[R]], None]]],
    ) -> None:
        super().__init__()
        self._f = f
        self._prx = prx
        self._dct: dict[Spec, ta.Optional[R]] = {}

    def __call__(self, ctx: C, spec: Spec) -> ta.Optional[R]:
        try:
            return self._dct[spec]
        except KeyError:
            pass
        p, sp = self._prx()
        self._dct[spec] = p
        try:
            r = self._f(ctx, spec)
            sp(r)
            return r
        finally:
            del self._dct[spec]


##


class CompositeFactory(Factory[R, C, A]):
    class Strategy(enum.Enum):
        FIRST = enum.auto()
        ONE = enum.auto()

    def __init__(self, *fs: Factory[R, C, A], strategy: Strategy = Strategy.FIRST) -> None:
        super().__init__()
        self._fs = fs
        self._st = strategy

    def __call__(self, ctx: C, arg: A) -> ta.Optional[R]:
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
