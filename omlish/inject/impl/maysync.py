# ruff: noqa: SLF001
import typing as ta

from ... import check
from ... import lang
from ..elements import CollectedElements
from ..injector import AsyncInjector
from ..inspect import KwargsTarget
from ..keys import as_key
from ..maysync import MaysyncInjector
from ..sync import Injector
from .injector import AsyncInjectorImpl


##


class MaysyncInjectorImpl(MaysyncInjector, lang.Final):
    _ai: AsyncInjector

    def try_provide(self, key: ta.Any) -> lang.Maybe[ta.Any]:
        return lang.run_maysync(self._ai.try_provide(key))

    def provide(self, key: ta.Any) -> ta.Any:
        return lang.run_maysync(self._ai.provide(key))

    def provide_kwargs(self, kt: KwargsTarget) -> ta.Mapping[str, ta.Any]:
        return lang.run_maysync(self._ai.provide_kwargs(kt))

    def inject(self, obj: ta.Any) -> ta.Any:
        return lang.run_maysync(self._ai.inject(obj))


def create_maysync_injector(ce: CollectedElements, p: MaysyncInjector | None = None) -> MaysyncInjector:
    ap: AsyncInjectorImpl | None = None
    if p is not None:
        ap = check.isinstance(check.isinstance(p, MaysyncInjectorImpl)._ai, AsyncInjectorImpl)

    si = MaysyncInjectorImpl()
    ai = AsyncInjectorImpl(
        ce,
        ap,
        internal_consts={
            as_key(MaysyncInjector): si,
            as_key(Injector): si,
        },
    )
    si._ai = ai
    lang.run_maysync(ai._init())
    return si
