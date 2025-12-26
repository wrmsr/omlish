import contextlib
import typing as ta

from .. import check
from .. import collections as col
from .. import dataclasses as dc
from .. import inject as inj
from .. import lang
from .base import AsyncLifecycle
from .base import Lifecycle
from .contextmanagers import async_lifecycle_context_manage
from .contextmanagers import lifecycle_context_manage
from .manager import AsyncLifecycleManager
from .manager import LifecycleManager
from .unwrap import unwrap_any_lifecycle


##


@ta.final
class _LifecycleRegistrar(lang.Final):
    def __init__(
            self,
            lifecycle_manager_cls: type[LifecycleManager | AsyncLifecycleManager],
            lifecycle_cls_tup: tuple[type[Lifecycle | AsyncLifecycle], ...],
            *,
            unwrap: bool = False,
    ) -> None:
        super().__init__()

        self._lifecycle_manager_cls = lifecycle_manager_cls
        self._lifecycle_cls_tup = lifecycle_cls_tup
        self._unwrap = unwrap

        self._seen: ta.MutableSet[ta.Any] = col.IdentityWeakSet()
        self._stack: list[_LifecycleRegistrar.State] = []

    @ta.final
    @dc.dataclass(frozen=True)
    class Dep(lang.Final):
        binding: inj.Binding | None
        obj: ta.Any
        lco: ta.Any

    @ta.final
    @dc.dataclass(frozen=True)
    class State(lang.Final):
        key: inj.Key
        deps: list['_LifecycleRegistrar.Dep'] = dc.field(default_factory=list)

    async def _on_provision(
            self,
            injector: inj.AsyncInjector,
            key: inj.Key,
            binding: inj.Binding | None,
            fn: ta.Callable[[], ta.Awaitable[ta.Any]],
    ) -> ta.Awaitable[ta.Any]:
        st = _LifecycleRegistrar.State(key)
        self._stack.append(st)
        try:
            obj = await fn()
        finally:
            popped = self._stack.pop()
            check.state(popped is st)

        lco: ta.Any
        if self._unwrap:
            lco = unwrap_any_lifecycle(obj)
        else:
            lco = obj

        if (
                lco is not None and
                isinstance(lco, self._lifecycle_cls_tup) and
                not isinstance(obj, self._lifecycle_manager_cls)
        ):
            if self._stack:
                self._stack[-1].deps.append(_LifecycleRegistrar.Dep(binding, obj, lco))

            if obj not in self._seen:
                mgr = await injector[self._lifecycle_manager_cls]

                dep_lcos = [d.lco for d in st.deps]

                if isinstance(mgr, AsyncLifecycleManager):
                    await mgr.add(lco, dep_lcos)
                elif isinstance(mgr, LifecycleManager):
                    mgr.add(lco, dep_lcos)
                else:
                    raise TypeError(mgr)

                self._seen.add(obj)

        elif self._stack:
            self._stack[-1].deps.extend(st.deps)

        return obj


def bind_lifecycle_registrar() -> inj.Elements:
    return inj.as_elements(
        inj.bind(_LifecycleRegistrar, to_const=(lr := _LifecycleRegistrar(
            LifecycleManager,
            (Lifecycle,),
            unwrap=True,
        ))),
        inj.bind_provision_listener(lr._on_provision),  # noqa
    )


def bind_async_lifecycle_registrar() -> inj.Elements:
    return inj.as_elements(
        inj.bind(_LifecycleRegistrar, to_const=(lr := _LifecycleRegistrar(
            AsyncLifecycleManager,
            (Lifecycle, AsyncLifecycle),
            unwrap=True,
        ))),
        inj.bind_provision_listener(lr._on_provision),  # noqa
    )


##


def bind_managed_lifecycle_manager(*, eager: bool | int = False) -> inj.Elements:
    # FIXME: lock?
    def inner(es: contextlib.ExitStack) -> LifecycleManager:
        return es.enter_context(lifecycle_context_manage(LifecycleManager()))

    return inj.as_elements(
        inj.bind(inner, singleton=True, eager=eager),
    )


def bind_async_managed_lifecycle_manager(*, eager: bool | int = False) -> inj.Elements:
    # FIXME: lock?
    async def inner(aes: contextlib.AsyncExitStack) -> AsyncLifecycleManager:
        return await aes.enter_async_context(async_lifecycle_context_manage(AsyncLifecycleManager()))

    return inj.as_elements(
        inj.bind(inner, singleton=True, eager=eager),
    )
