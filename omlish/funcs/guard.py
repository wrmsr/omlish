import functools
import typing as ta

from .. import check
from .. import collections as col


T = ta.TypeVar('T')
T_co = ta.TypeVar('T_co', covariant=True)
P = ta.ParamSpec('P')


##


class GuardFn(ta.Protocol[P, T_co]):
    def __get__(self, instance, owner=None) -> ta.Self: ...

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> ta.Callable[[], T_co] | None: ...


##


@ta.final
class DumbGuardFn(ta.Generic[P, T]):
    def __init__(self, fn: ta.Callable[P, T]) -> None:
        self._fn = fn

    def __get__(self, instance, owner=None):
        return DumbGuardFn(self._fn.__get__(instance, owner))  # noqa

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> ta.Callable[[], T]:
        return functools.partial(self._fn, *args, **kwargs)


dumb = DumbGuardFn


##


class AmbiguousGuardFnError(Exception):
    pass


@ta.final
class MultiGuardFn(ta.Generic[P, T]):
    def __init__(
            self,
            *children: GuardFn[P, T],
            strict: bool = False,
    ) -> None:
        self._children, self._strict = children, strict

    def __get__(self, instance, owner=None):
        return MultiGuardFn(*[c.__get__(instance, owner) for c in self._children], strict=self._strict)  # noqa

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> ta.Callable[[], T] | None:
        matches = []
        for c in self._children:
            if (m := c(*args, **kwargs)) is not None:
                if not self._strict:
                    return m
                matches.append(m)
        if not matches:
            return None
        elif len(matches) > 1:
            raise AmbiguousGuardFnError
        else:
            return matches[0]


multi = MultiGuardFn


##


class GuardFnMethod(ta.Generic[P, T]):
    def __init__(
            self,
            *,
            strict: bool = False,
            requires_override: bool = False,
    ) -> None:
        super().__init__()

        self._strict = strict

        self._registry: col.AttrRegistry[ta.Callable, None] = col.AttrRegistry(
            requires_override=requires_override,
        )

        self._cache: col.AttrRegistryCache[ta.Callable, None, MultiGuardFn] = col.AttrRegistryCache(
            self._registry,
            self._prepare,
        )

        self._owner: type | None = None
        self._name: str | None = None

    def __set_name__(self, owner, name):
        if self._owner is None:
            self._owner = owner
        if self._name is None:
            self._name = name

    def register(self, fn: T) -> T:
        check.callable(fn)
        self._registry.register(ta.cast(ta.Callable, fn), None)
        return fn

    def _prepare(self, instance_cls: type, collected: ta.Mapping[str, tuple[ta.Callable, None]]) -> MultiGuardFn:
        return MultiGuardFn(
            *[getattr(instance_cls, a) for a in collected],
            strict=self._strict,
        )

    def __get__(self, instance, owner=None):
        if instance is None:
            return self

        func = self._cache.get(type(instance))
        return func.__get__(instance, owner)  # noqa

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        instance, *rest = args
        func = self._cache.get(type(instance))
        return func.__get__(instance)(*rest, **kwargs)  # noqa


method = GuardFnMethod
