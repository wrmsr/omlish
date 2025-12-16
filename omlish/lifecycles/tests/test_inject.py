"""
TODO:
 - *external* Lifecycles - objs themselves hide their lc's
"""
import typing as ta

from ... import check
from ... import collections as col
from ... import dataclasses as dc
from ... import inject as inj
from ... import lang
from ..base import AsyncLifecycle
from ..base import Lifecycle
from ..contextmanagers import LifecycleContextManager
from ..manager import AsyncLifecycleManager
from ..manager import LifecycleManager


##


@ta.final
class _LifecycleRegistrar(lang.Final):
    def __init__(
            self,
            lifecycle_manager_cls: type[LifecycleManager | AsyncLifecycleManager],
            lifecycle_cls_tup: tuple[type[Lifecycle | AsyncLifecycle], ...],
    ) -> None:
        super().__init__()

        self._lifecycle_manager_cls = lifecycle_manager_cls
        self._lifecycle_cls_tup = lifecycle_cls_tup

        self._seen: ta.MutableSet[ta.Any] = col.IdentityWeakSet()
        self._stack: list[_LifecycleRegistrar.State] = []

    @ta.final
    @dc.dataclass(frozen=True)
    class Dep(lang.Final):
        binding: inj.Binding | None
        obj: ta.Any

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

        if (
                isinstance(obj, self._lifecycle_cls_tup) and
                not isinstance(obj, self._lifecycle_manager_cls)
        ):
            if self._stack:
                self._stack[-1].deps.append(_LifecycleRegistrar.Dep(binding, obj))

            if obj not in self._seen:
                mgr = await injector[self._lifecycle_manager_cls]

                dep_objs = [d.obj for d in st.deps]

                if isinstance(mgr, AsyncLifecycleManager):
                    await mgr.add(obj, dep_objs)
                elif isinstance(mgr, LifecycleManager):
                    mgr.add(obj, dep_objs)
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
        ))),
        inj.bind_provision_listener(lr._on_provision),  # noqa
    )


##


class DumbLifecycle(Lifecycle):
    def lifecycle_construct(self) -> None:
        print(f'{self}.lifecycle_construct')

    def lifecycle_start(self) -> None:
        print(f'{self}.lifecycle_start')

    def lifecycle_stop(self) -> None:
        print(f'{self}.lifecycle_stop')

    def lifecycle_destroy(self) -> None:
        print(f'{self}.lifecycle_destroy')


@dc.dataclass()
class Db(DumbLifecycle):
    pass


@dc.dataclass()
class ServiceA(DumbLifecycle):
    db: Db
    i: int


@dc.dataclass()
class ServiceB(DumbLifecycle):
    db: Db


@dc.dataclass()
class ServiceC(DumbLifecycle):
    a: ServiceA
    b: ServiceB
    db: Db


def test_inject():
    with inj.create_managed_injector(
        bind_lifecycle_registrar(),
            inj.bind(LifecycleManager, singleton=True, eager=True),

            inj.bind(Db, singleton=True),
            inj.bind(ServiceA, singleton=True),
            inj.bind(ServiceB, singleton=True),
            inj.bind(ServiceC, singleton=True, eager=True),

            inj.bind(420),
    ) as i:  # noqa
        print()
        with LifecycleContextManager(i[LifecycleManager].lifecycle):
            print(i[ServiceC])
