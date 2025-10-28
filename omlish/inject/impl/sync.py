import typing as ta

from ... import lang
from ..elements import CollectedElements
from ..injector import AsyncInjector
from ..inspect import KwargsTarget
from ..keys import Key
from ..sync import Injector
from .injector import AsyncInjectorImpl


##


class InjectorImpl(Injector, lang.Final):
    _ai: AsyncInjector

    def try_provide(self, key: ta.Any) -> lang.Maybe[ta.Any]:
        return lang.sync_await(self._ai.try_provide(key))

    def provide(self, key: ta.Any) -> ta.Any:
        return lang.sync_await(self._ai.provide(key))

    def provide_kwargs(self, kt: KwargsTarget) -> ta.Mapping[str, ta.Any]:
        return lang.sync_await(self._ai.provide_kwargs(kt))

    def inject(self, obj: ta.Any) -> ta.Any:
        return lang.sync_await(self._ai.inject(obj))


def create_injector(ce: CollectedElements) -> Injector:
    si = InjectorImpl()
    ai = AsyncInjectorImpl(
        ce,
        internal_consts={
            Key(Injector): si,
        },
    )
    si._ai = ai  # noqa
    lang.sync_await(ai._init())  # noqa
    return si
