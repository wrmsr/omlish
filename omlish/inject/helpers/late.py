"""
A minor tidiness for hiding refs to [Async]Injector in circ-dep workarounds. Unfortunately unsuitable outside of
injection modules due to it itself being in here (as user code shouldn't reference injector guts), but at least it's
something.

TODO:
 - annotations lol
 - some kind of stdlib/langy auto interoppy thingy? ala Provider[T]?
  - nothing really in stdlib
"""
import abc
import functools
import typing as ta

from ... import lang
from ..binder import bind
from ..elements import Elements
from ..elements import as_elements
from ..injector import AsyncInjector
from ..inspect import KwargsTarget
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


def bind_late(cls: ta.Any) -> Elements:
    return as_elements(
        bind(Late[cls], to_fn=KwargsTarget.of(  # noqa
            lambda i: functools.partial(i.provide, cls),
            i=Injector,
        )),
    )


def bind_async_late(cls: ta.Any) -> Elements:
    return as_elements(
        bind(AsyncLate[cls], to_fn=KwargsTarget.of(  # noqa
            lambda i: functools.partial(i.provide, cls),
            i=AsyncInjector,
        )),
    )
