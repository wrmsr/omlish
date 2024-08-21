import dataclasses as dc
import threading
import typing as ta

from .. import check
from .. import matchfns as mfs
from .. import reflect as rfl


R = ta.TypeVar('R')
C = ta.TypeVar('C')


##


@dc.dataclass(frozen=True)
class TypeMapFactory(mfs.MatchFn[[C, rfl.Type], R]):
    m: ta.Mapping[rfl.Type, R] = dc.field(default_factory=dict)

    def __post_init__(self) -> None:
        for k in self.m:
            if not isinstance(k, rfl.TYPES):
                raise TypeError(k)

    def guard(self, ctx: C, rty: rfl.Type) -> bool:
        check.isinstance(rty, rfl.TYPES)
        return rty in self.m

    def fn(self, ctx: C, rty: rfl.Type) -> R:
        check.isinstance(rty, rfl.TYPES)
        try:
            return self.m[rty]
        except KeyError:
            raise mfs.MatchGuardError(ctx, rty)  # noqa


##


class TypeCacheFactory(mfs.MatchFn[[C, rfl.Type], R]):
    def __init__(self, f: mfs.MatchFn[[C, rfl.Type], R]) -> None:
        super().__init__()
        self._f = f
        self._dct: dict[rfl.Type, R | None] = {}
        self._mtx = threading.RLock()

    def guard(self, ctx: C, rty: rfl.Type) -> bool:
        check.isinstance(rty, rfl.TYPES)
        with self._mtx:
            try:
                e = self._dct[rty]
            except KeyError:
                if self._f.guard(ctx, rty):
                    return True
                else:
                    self._dct[rty] = None
                    return False
            else:
                return e is not None

    def fn(self, ctx: C, rty: rfl.Type) -> R:
        check.isinstance(rty, rfl.TYPES)
        with self._mtx:
            try:
                e = self._dct[rty]
            except KeyError:
                try:
                    ret = self._f(ctx, rty)
                except mfs.MatchGuardError:
                    self._dct[rty] = None
                    raise
                else:
                    self._dct[rty] = ret
                    return ret
            else:
                if e is None:
                    raise mfs.MatchGuardError(ctx, rty)
                else:
                    return e


##


class RecursiveTypeFactory(mfs.MatchFn[[C, rfl.Type], R]):
    def __init__(
            self,
            f: mfs.MatchFn[[C, rfl.Type], R],
            prx: ta.Callable[[], tuple[R, ta.Callable[[R], None]]],
    ) -> None:
        super().__init__()
        self._f = f
        self._prx = prx
        self._dct: dict[rfl.Type, R] = {}

    def guard(self, ctx: C, rty: rfl.Type) -> bool:
        check.isinstance(rty, rfl.TYPES)
        return self._f.guard(ctx, rty)

    def fn(self, ctx: C, rty: rfl.Type) -> R:
        check.isinstance(rty, rfl.TYPES)
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
