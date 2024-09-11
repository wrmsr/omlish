"""
TODO:
 - unify MatchFnClass with dispatch.method?
  - __call__ = mfs.method(); @__call__.register(lambda: ...) def _call_... ?
  - not really the same thing, dispatch is unordered this is necessarily ordered
"""
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

    def __get__(self, instance, owner=None):
        return self

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

    def __get__(self, instance, owner=None):
        return self.__class__(
            self._guard.__get__(instance, owner),  # noqa
            self._fn.__get__(instance, owner),  # noqa
        )


@ta.overload
def simple(guard: ta.Callable[..., bool], fn: ta.Callable[P, T]) -> SimpleMatchFn[P, T]:
    ...


@ta.overload
def simple(guard: ta.Callable[..., bool]) -> ta.Callable[[ta.Callable[P, T]], SimpleMatchFn[P, T]]:
    ...


def simple(guard, fn=None):
    def inner(fn):  # noqa
        return SimpleMatchFn(guard, fn)
    if fn is not None:
        return inner(fn)
    else:
        return inner


##


class AmbiguousMatchesError(Exception):
    pass


@dc.dataclass(frozen=True)
class MultiMatchFn(MatchFn[P, T]):
    children: ta.Sequence[MatchFn[P, T]]
    strict: bool = False

    def match(self, *args: P.args, **kwargs: P.kwargs) -> MatchFn[P, T] | None:
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
        return self.match(*args, **kwargs) is not None

    def fn(self, *args: P.args, **kwargs: P.kwargs) -> T:
        if (m := self.match(*args, **kwargs)) is None:
            raise MatchGuardError(*args, **kwargs)
        return m.fn(*args, **kwargs)

    def __get__(self, instance, owner=None):
        return self.__class__(
            [c.__get__(instance, owner) for c in self.children],
            strict=self.strict,
        )


def multi(*children: MatchFn[P, T], strict: bool = False) -> MultiMatchFn:  # MultiMatchFn[P[0], T[-1]]
    return MultiMatchFn(children, strict=strict)  # noqa


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
            lock: lang.DefaultLockable = None,
    ) -> None:
        super().__init__()
        self._f = f
        self._key = key
        self._lock = lock
        self._lock_impl = lang.default_lock(lock)()
        self._dct: dict[ta.Any, lang.Maybe[ta.Any]] = {}

    def guard(self, *args: P.args, **kwargs: P.kwargs) -> bool:
        with self._lock_impl:
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
        with self._lock_impl:
            k = self._key(*args, **kwargs)
            try:
                e = self._dct[k]
            except KeyError:
                try:
                    ret = self._f(*args, **kwargs)
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

    def __get__(self, instance, owner=None):
        return self.__class__(self._f.__get__(instance, owner), key=self._key)  # noqa


cached = CachedMultiFn


##


class MatchFnClass(MatchFn[P, T]):
    _cls_match_fn: ta.ClassVar[MultiMatchFn]

    def __init__(self) -> None:
        super().__init__()
        self.__match_fn: MatchFn[P, T] | None = None

    @property
    def _match_fn(self) -> MatchFn[P, T]:
        if (mf := self.__match_fn) is None:
            mf = self.__match_fn = self._cls_match_fn.__get__(self)
        return mf

    def __init_subclass__(cls, strict: bool = False, **kwargs: ta.Any) -> None:
        super().__init_subclass__()
        if '_cls_match_fn' in cls.__dict__:
            raise AttributeError('_cls_match_fn')
        d = {}
        for c in cls.__mro__:
            for a, o in c.__dict__.items():
                if isinstance(o, MatchFn) and a not in d:
                    d[a] = o
        cls._cls_match_fn = MultiMatchFn(list(d.values()), strict=strict)

    def guard(self, *args: P.args, **kwargs: P.kwargs) -> bool:
        return self._match_fn.guard(*args, **kwargs)

    def fn(self, *args: P.args, **kwargs: P.kwargs) -> T:
        return self._match_fn.fn(*args, **kwargs)
