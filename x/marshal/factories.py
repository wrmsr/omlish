import abc
import dataclasses as dc
import threading
import typing as ta

from .specs import Spec


R = ta.TypeVar('R')
C = ta.TypeVar('C')
A = ta.TypeVar('A')


class Factory(abc.ABC, ta.Generic[R, C, A]):
    @abc.abstractmethod
    def __call__(self, ctx: C, arg: A) -> ta.Optional[R]:
        raise NotImplementedError


@dc.dataclass(frozen=True)
class FuncFactory(ta.Generic[R, C, A]):
    fn: ta.Callable[[C, A], ta.Optional[R]]

    def __call__(self, ctx: C, arg: A) -> ta.Optional[R]:
        return self.fn(ctx, arg)


@dc.dataclass(frozen=True)
class SpecMapFactory(Factory[R, C]):
    m: ta.Mapping[Spec, R] = dc.field(default_factory=dict)

    def __call__(self, ctx: C, spec: Spec) -> ta.Optional[R]:
        return self.m.get(spec)


class SpecCacheFactory(Factory[R, C]):
    def __init__(self, f: Factory[R, C, Spec]) -> None:
        super().__init__()
        self._f = f
        self._dct: ta.Dict[Spec, ta.Optional[R]] = {}
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


class RecursiveSpecFactory(Factory[R, C]):
    def __int__(self, f: Factory[R, C]) -> None:
        super().__init__()
        self._f = f
        self._dct: ta.Dict[Spec, ta.Optional[R]] = {}

    def __call__(self, ctx: C, spec: Spec) -> ta.Optional[R]:
        """
        if r, ok := f.m[a]; ok {
            return r, nil
        }
        p, sp := f.p()
        f.m[a] = p
        defer delete(f.m, a)
        i, err := f.f.Make(ctx, a)
        if err != nil {
            var z R
            return z, err
        }
        sp(i)
        """
