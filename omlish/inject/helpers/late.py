"""
A minor tidiness for hiding refs to [Async]Injector in circ-dep workarounds. Unfortunately unsuitable outside of
injection modules due to it itself being in here (as user code shouldn't reference injector guts), but at least it's
something.
"""
import abc
import functools
import typing as ta

from ... import lang
from ... import reflect as rfl
from ..binder import bind
from ..elements import Elements
from ..elements import as_elements
from ..injector import AsyncInjector
from ..inspect import KwargsTarget
from ..keys import Key
from ..keys import as_key
from ..sync import Injector


T = ta.TypeVar('T')


##


class Late(lang.Abstract, ta.Generic[T]):
    @abc.abstractmethod
    def __call__(self) -> T:
        raise NotImplementedError


class AsyncLate(lang.Abstract, ta.Generic[T]):
    @abc.abstractmethod
    def __call__(self) -> ta.Awaitable[T]:
        raise NotImplementedError


#


def _bind_late(
        injector_cls: type,
        late_cls: ta.Any,
        inner: ta.Any,
        outer: ta.Any | None = None,
) -> Elements:
    inner_key = as_key(inner)

    outer_key: Key
    outer_fac: ta.Callable[[ta.Any], ta.Any]
    if outer is None:
        inner_ann = rfl.to_annotation(inner_key.ty)
        outer_ann = late_cls[inner_ann]
        outer_key = Key(rfl.type_(outer_ann), tag=inner_key.tag)
        outer_fac = lang.identity
    else:
        outer_key = as_key(outer)
        outer_cls = rfl.get_concrete_type(outer_key.ty)
        outer_fac = outer_cls  # type: ignore[assignment]

    return as_elements(
        bind(outer_key, to_fn=KwargsTarget.of(  # noqa
            lambda i: outer_fac(functools.partial(i.provide, inner_key)),
            i=injector_cls,
        )),
    )


def bind_late(inner: ta.Any, outer: ta.Any | None = None) -> Elements:
    return _bind_late(Injector, Late, inner, outer)


def bind_async_late(inner: ta.Any, outer: ta.Any | None = None) -> Elements:
    return _bind_late(AsyncInjector, AsyncLate, inner, outer)
