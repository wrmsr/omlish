import abc
import dataclasses as dc
import typing as ta

from . import lang


T = ta.TypeVar('T')
P = ta.ParamSpec('P')


##


class MatchGuardError(Exception):
    pass


class MatchFn(abc.ABC, ta.Generic[P, T]):
    @abc.abstractmethod
    def guard(self, *args: P.args, **kwargs: P.kwargs) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def fn(self, *args: P.args, **kwargs: P.kwargs) -> T:
        raise NotImplementedError

    @ta.final
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        if not self.guard(*args, **kwargs):
            raise MatchGuardError(*args, **kwargs)
        return self.fn(*args, **kwargs)


##


@dc.dataclass(frozen=True)
class SimpleMatchFn(MatchFn[P, T]):
    _guard: ta.Callable[P, bool]
    _fn: ta.Callable[P, T]

    def guard(self, *args: P.args, **kwargs: P.kwargs) -> bool:
        return self._guard(*args, **kwargs)

    def fn(self, *args: P.args, **kwargs: P.kwargs) -> T:
        return self._fn(*args, **kwargs)


simple = SimpleMatchFn


##


class AmbiguousMatchesError(Exception):
    pass


@dc.dataclass(frozen=True)
class MultiMatchFn(MatchFn[P, T]):
    children: ta.Sequence[MatchFn[P, T]]
    strict: bool = False

    def _match(self, *args: P.args, **kwargs: P.kwargs) -> MatchFn[P, T] | None:
        matches = []
        for cur in self.children:
            if cur.guard(*args, **kwargs):
                if self.strict:
                    matches.append(cur)
                else:
                    return cur
        if not matches:
            return None
        elif len(matches) > 1:
            raise AmbiguousMatchesError
        else:
            return matches[0]

    def guard(self, *args: P.args, **kwargs: P.kwargs) -> bool:
        return self._match(*args, **kwargs) is not None

    def fn(self, *args: P.args, **kwargs: P.kwargs) -> T:
        if (m := self._match(*args, **kwargs)) is None:
            raise MatchGuardError(*args, **kwargs)
        return m.fn(*args, **kwargs)


def multi(*children: MatchFn[P, T], strict: bool = False):
    return MultiMatchFn(children, strict=strict)


##


class CachedMultiFn(MatchFn[P, T]):
    @staticmethod
    def _default_key(*args, **kwargs):
        return (args, tuple(sorted(kwargs.items(), key=lambda t: t[0])))

    def __init__(
            self,
            f: MatchFn[P, T],
            *,
            key: ta.Callable[P, ta.Any] = _default_key,
    ) -> None:
        super().__init__()
        self._f = f
        self._dct: dict[ta.Any, lang.Maybe[ta.Any]] = {}
        self._key = key

    def guard(self, *args: P.args, **kwargs: P.kwargs) -> bool:
        k = self._key(*args, **kwargs)
        try:
            e = self._dct[k]
        except KeyError:
            if self._f.guard(*args, **kwargs):
                return True
            else:
                self._dct[k] = lang.empty()
                return False
        else:
            return e.present

    def fn(self, *args: P.args, **kwargs: P.kwargs) -> T:
        k = self._key(*args, **kwargs)
        try:
            e = self._dct[k]
        except KeyError:
            try:
                ret = self._f.fn(*args, **kwargs)
            except MatchGuardError:
                self._dct[k] = lang.empty()
                raise
            else:
                self._dct[k] = lang.just(ret)
                return ret
        else:
            if e.present:
                return e.must()
            else:
                raise MatchGuardError(*args, **kwargs)
