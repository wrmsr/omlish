# ruff: noqa: SLF001
import typing as ta

from omlish import check
from omlish import lang
from omlish.inject.elements import CollectedElements
from omlish.inject.impl.injector import AsyncInjectorImpl
from omlish.inject.injector import AsyncInjector
from omlish.inject.inspect import KwargsTarget
from omlish.inject.keys import as_key
from omlish.inject.sync import Injector

from ...maysync import run_maysync
from ..maysync import MaysyncInjector


##


class MaysyncInjectorImpl(MaysyncInjector, lang.Final):
    _ai: AsyncInjector

    def try_provide(self, key: ta.Any) -> lang.Maybe[ta.Any]:
        return run_maysync(self._ai.try_provide(key))

    def provide(self, key: ta.Any) -> ta.Any:
        return run_maysync(self._ai.provide(key))

    def provide_kwargs(self, kt: KwargsTarget) -> ta.Mapping[str, ta.Any]:
        return run_maysync(self._ai.provide_kwargs(kt))

    def inject(self, obj: ta.Any) -> ta.Any:
        return run_maysync(self._ai.inject(obj))


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
    run_maysync(ai._init())
    return si
