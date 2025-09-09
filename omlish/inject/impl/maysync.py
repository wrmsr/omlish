import typing as ta

from ... import lang
from ..elements import Elements
from ..injector import AsyncInjector
from ..injector import Injector
from ..inspect import KwargsTarget
from ..keys import Key
from .elements import ElementCollection
from .injector import AsyncInjectorImpl


##


class MaysyncInjector(Injector, lang.Final):
    _ai: AsyncInjector

    def try_provide(self, key: ta.Any) -> lang.Maybe[ta.Any]:
        return lang.run_maysync(self._ai.try_provide(key))

    def provide(self, key: ta.Any) -> ta.Any:
        return lang.run_maysync(self._ai.provide(key))

    def provide_kwargs(self, kt: KwargsTarget) -> ta.Mapping[str, ta.Any]:
        return lang.run_maysync(self._ai.provide_kwargs(kt))

    def inject(self, obj: ta.Any) -> ta.Any:
        return lang.run_maysync(self._ai.inject(obj))


def create_injector(es: Elements) -> Injector:
    mi = MaysyncInjector()
    ai = AsyncInjectorImpl(ElementCollection(es), internal_consts={Key(Injector): mi})
    mi._ai = ai  # noqa
    lang.run_maysync(ai._init())  # noqa
    return mi
