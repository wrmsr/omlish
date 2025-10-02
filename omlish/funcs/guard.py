import abc
import functools
import operator
import typing as ta

from .. import check
from .. import collections as col
from .. import lang


T = ta.TypeVar('T')
T_co = ta.TypeVar('T_co', covariant=True)
U = ta.TypeVar('U')
P = ta.ParamSpec('P')


##


class GuardFn(ta.Protocol[P, T_co]):
    def __get__(self, instance, owner=None): ...

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
            default: GuardFn[P, T] | None = None,
            strict: bool = False,
    ) -> None:
        self._children, self._default, self._strict = children, default, strict

    lang.attr_ops(lambda self: (
        self._children,
        self._default,
        self._strict,
    )).install(locals())

    def __get__(self, instance, owner=None):
        return MultiGuardFn(*map(operator.methodcaller('__get__', instance, owner), self._children), default=self._default.__get__(instance, owner) if self._default is not None else None, strict=self._strict)  # noqa

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> ta.Callable[[], T] | None:
        matches = []
        for c in self._children:
            if (m := c(*args, **kwargs)) is not None:
                if not self._strict:
                    return m
                matches.append(m)
        if not matches:
            if (dfl := self._default) is not None:
                return dfl(*args, **kwargs)
            else:
                return None
        elif len(matches) > 1:
            raise AmbiguousGuardFnError
        else:
            return matches[0]


multi = MultiGuardFn


##


class _BaseGuardFnMethod(lang.Abstract, ta.Generic[P, T]):
    def __init__(
            self,
            *,
            strict: bool = False,
            requires_override: bool = False,
            instance_cache: bool = False,
            default: GuardFn[P, T] | None = None,
    ) -> None:
        super().__init__()

        self._strict = strict
        self._instance_cache = instance_cache
        self._default = default

        self._registry: col.AttrRegistry[ta.Callable, None] = col.AttrRegistry(
            requires_override=requires_override,
        )

        self._cache: col.AttrRegistryCache[ta.Callable, None, MultiGuardFn] = col.AttrRegistryCache(
            self._registry,
            self._prepare,
        )

    _owner: type | None = None
    _name: str | None = None

    def __set_name__(self, owner, name):
        if self._owner is None:
            self._owner = owner
        if self._name is None:
            self._name = name

    def register(self, fn: U) -> U:
        check.callable(fn)
        self._registry.register(ta.cast(ta.Callable, fn), None)
        return fn

    def _prepare(self, instance_cls: type, collected: ta.Mapping[str, tuple[ta.Callable, None]]) -> MultiGuardFn:
        return MultiGuardFn(
            *[getattr(instance_cls, a) for a in collected],
            default=self._default,
            strict=self._strict,
        )

    @abc.abstractmethod
    def _bind(self, instance, owner):
        raise NotImplementedError

    def __get__(self, instance, owner=None):
        if instance is None:
            return self

        if self._instance_cache:
            try:
                return instance.__dict__[self._name]
            except KeyError:
                pass

        bound = self._bind(instance, owner)

        if self._instance_cache:
            instance.__dict__[self._name] = bound

        return bound

    def _call(self, *args, **kwargs):
        instance, *rest = args
        return self.__get__(instance)(*rest, **kwargs)

#


@ta.final
class GuardFnMethod(_BaseGuardFnMethod[P, T]):
    def _bind(self, instance, owner):
        return self._cache.get(type(instance)).__get__(instance, owner)  # noqa

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> ta.Callable[[], T] | None:
        return self._call(*args, **kwargs)


def method(
        *,
        strict: bool = False,
        requires_override: bool = False,
        instance_cache: bool = False,
        default: bool = False,
) -> ta.Callable[[ta.Callable[P, T]], GuardFnMethod[P, T]]:  # noqa
    def inner(fn):
        return GuardFnMethod(
            strict=strict,
            requires_override=requires_override,
            instance_cache=instance_cache,
            default=fn if default else None,
        )

    return inner


#


@ta.final
class ImmediateGuardFnMethod(_BaseGuardFnMethod[P, T]):
    def _bind(self, instance, owner):
        gf = self._cache.get(type(instance)).__get__(instance, owner)  # noqa

        def inner(*args, **kwargs):
            return gf(*args, **kwargs)()  # Note: cannot be None due to non-optional default

        return inner

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        return self._call(*args, **kwargs)


def immediate_method(
        *,
        strict: bool = False,
        requires_override: bool = False,
        instance_cache: bool = False,
) -> ta.Callable[[ta.Callable[P, T]], ImmediateGuardFnMethod[P, T]]:  # noqa
    def inner(fn):
        return ImmediateGuardFnMethod(
            strict=strict,
            requires_override=requires_override,
            instance_cache=instance_cache,
            default=(lambda *args, **kwargs: lambda: fn(*args, **kwargs)),
        )

    return inner
