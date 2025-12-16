"""
TODO:
 - annotations lol
 - some kind of stdlib/langy auto interoppy thingy? ala Provider[T]?
  - nothing really in stdlib
"""
import abc
import functools
import typing as ta

from omlish import lang
from omlish import inject as inj


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


def bind_late(cls: ta.Any) -> inj.Elements:
    return inj.as_elements(
        inj.bind(Late[cls], to_fn=inj.KwargsTarget.of(  # noqa
            lambda i: functools.partial(i.provide, cls),
            i=inj.Injector,
        )),
    )


def bind_async_late(cls: ta.Any) -> inj.Elements:
    return inj.as_elements(
        inj.bind(AsyncLate[cls], to_fn=inj.KwargsTarget.of(  # noqa
            lambda i: functools.partial(i.provide, cls),
            i=inj.AsyncInjector,
        )),
    )


##


