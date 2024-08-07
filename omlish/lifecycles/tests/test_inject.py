import typing as ta
import weakref

from ... import check
from ... import dataclasses as dc
from ... import inject as inj
from ... import lang
from ..base import Lifecycle
from ..manager import LifecycleManager


##


class _LifecycleRegistrar(lang.Final):

    def __init__(self) -> None:
        super().__init__()

        self._seen: ta.MutableSet[ta.Any] = weakref.WeakSet()
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
        st = self.State(key)
        self._stack.append(st)
        try:
            instance = fn()
        finally:
            popped = self._stack.pop()
            check.state(popped is st)

        if isinstance(instance, Lifecycle) and not isinstance(instance, LifecycleManager):
            if self._stack:
                self._stack[-1].deps.append(_LifecycleRegistrar.Dep(binding, instance))

            if instance not in self._seen:
                man_key = inj.Key(LifecycleManager)
                man: LifecycleManager = injector.provide(man_key)
                dep_objs = [d.obj for d in st.deps]
                man.add(instance, dep_objs)
                self._seen.add(instance)

        elif self._stack:
            self._stack[-1].deps.extend(st.deps)

        return instance


##


@dc.dataclass(frozen=True)
class Db:
    pass


@dc.dataclass(frozen=True)
class ServiceA:
    db: Db


@dc.dataclass(frozen=True)
class ServiceB:
    db: Db


@dc.dataclass(frozen=True)
class ServiceB:
    a: ServiceA
    b: ServiceB
    db: Db


def test_inject():
    lr = _LifecycleRegistrar()
    with inj.create_managed_injector(
        inj.bind(_LifecycleRegistrar, to_const=lr),
        inj.bind_provision_listener(lr._on_provision),
    ) as i:  # noqa
        pass
