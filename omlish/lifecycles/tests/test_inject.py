"""
TODO:
 - ** WeakIdentitySet **
 - *external* Lifecycles - objs themselves hide their lc's
"""
import typing as ta
import weakref

from ... import check
from ... import collections as col
from ... import dataclasses as dc
from ... import inject as inj
from ... import lang
from ..base import Lifecycle
from ..contextmanagers import LifecycleContextManager
from ..manager import LifecycleManager


##


def _new_weak_identity_set():
    s = weakref.WeakSet()
    s.data = col.IdentitySet()
    return s


class _LifecycleRegistrar(lang.Final):

    def __init__(self) -> None:
        super().__init__()

        self._seen: ta.MutableSet[ta.Any] = _new_weak_identity_set()
        self._stack: list[_LifecycleRegistrar.State] = []

    @dc.dataclass(frozen=True)
    class Dep(lang.Final):
        binding: inj.Binding
        obj: ta.Any

    @dc.dataclass(frozen=True)
    class State(lang.Final):
        key: inj.Key
        deps: list['_LifecycleRegistrar.Dep'] = dc.field(default_factory=list)

    def _on_provision(
            self,
            injector: inj.Injector,
            key: inj.Key,
            binding: inj.Binding,
            fn: ta.Callable[[], ta.Any],
    ) -> ta.Callable[[], ta.Any]:
        st = _LifecycleRegistrar.State(key)
        self._stack.append(st)
        try:
            obj = fn()
        finally:
            popped = self._stack.pop()
            check.state(popped is st)

        if isinstance(obj, Lifecycle) and not isinstance(obj, LifecycleManager):
            if self._stack:
                self._stack[-1].deps.append(_LifecycleRegistrar.Dep(binding, obj))

            if obj not in self._seen:
                mgr = injector[LifecycleManager]
                dep_objs = [d.obj for d in st.deps]
                mgr.add(obj, dep_objs)
                self._seen.add(obj)

        elif self._stack:
            self._stack[-1].deps.extend(st.deps)

        return obj


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
class Db(Lifecycle):
    pass


@dc.dataclass()
class ServiceA(Lifecycle):
    db: Db
    i: int


@dc.dataclass()
class ServiceB(Lifecycle):
    db: Db


@dc.dataclass()
class ServiceC(Lifecycle):
    a: ServiceA
    b: ServiceB
    db: Db


def test_inject():
    lr = _LifecycleRegistrar()
    with inj.create_managed_injector(
            inj.bind(_LifecycleRegistrar, to_const=lr),
            inj.bind_provision_listener(lr._on_provision),

            inj.bind(LifecycleManager, singleton=True, eager=True),

            inj.bind(Db, singleton=True),
            inj.bind(ServiceA, singleton=True),
            inj.bind(ServiceB, singleton=True),
            inj.bind(ServiceC, singleton=True, eager=True),

            inj.bind(420),
    ) as i:  # noqa
        with LifecycleContextManager(i[LifecycleManager].controller):
            print(i[ServiceC])
