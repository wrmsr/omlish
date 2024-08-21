import dataclasses as dc
import threading
import typing as ta

from .. import matchfns as mfs
from .. import reflect as rfl


R = ta.TypeVar('R')
C = ta.TypeVar('C')


##


@dc.dataclass(frozen=True)
class TypeMapFactory(mfs.MatchFn[[C, rfl.Type], R]):
    m: ta.Mapping[rfl.Type, R] = dc.field(default_factory=dict)

    def guard(self, ctx: C, ty: rfl.Type) -> bool:
        return ty in self.m

    def fn(self, ctx: C, ty: rfl.Type) -> R:
        try:
            return self.m[ty]
        except KeyError:
            raise mfs.MatchGuardError(ctx, ty)  # noqa


##


class TypeCacheFactory(mfs.MatchFn[[C, rfl.Type], R]):
    def __init__(self, f: mfs.MatchFn[[C, rfl.Type], R]) -> None:
        super().__init__()
        self._f = f
        self._dct: dict[rfl.Type, R | None] = {}
        self._mtx = threading.RLock()

    def guard(self, ctx: C, ty: rfl.Type) -> bool:
        with self._mtx:
            try:
                e = self._dct[ty]
            except KeyError:
                if self._f.guard(ctx, ty):
                    return True
                else:
                    self._dct[ty] = None
                    return False
            else:
                return e is not None

    def fn(self, ctx: C, ty: rfl.Type) -> R:
        with self._mtx:
            try:
                e = self._dct[ty]
            except KeyError:
                try:
                    ret = self._f(ctx, ty)
                except mfs.MatchGuardError:
                    self._dct[ty] = None
                    raise
                else:
                    self._dct[ty] = ret
                    return ret
            else:
                if e is None:
                    raise mfs.MatchGuardError(ctx, ty)
                else:
                    return e


##


class RecursiveTypeFactory(mfs.MatchFn[[C, rfl.Type], R]):
    def __init__(
            self,
            f: mfs.MatchFn[[C, rfl.Type], R],
            prx: ta.Callable[[], tuple[R | None, ta.Callable[[R | None], None]]],
    ) -> None:
        super().__init__()
        self._f = f
        self._prx = prx
        self._dct: dict[rfl.Type, R] = {}

    def guard(self, ctx: C, ty: rfl.Type) -> bool:
        return self._f.guard(ctx, ty)

    def fn(self, ctx: C, rty: rfl.Type) -> R:
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
