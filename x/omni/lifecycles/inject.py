import typing as ta
import weakref

from .. import check
from .. import dataclasses as dc
from .. import inject as inj
from .manager import LifecycleManager
from .types import Lifecycle


class _LifecycleRegistrar:

    def __init__(self) -> None:
        super().__init__()

        self._seen: ta.MutableSet[ta.Any] = weakref.WeakSet()
        self._stack: ta.List[_LifecycleRegistrar.State] = []

    class State(dc.Pure):
        key: inj.Key
        dependencies: ta.List[ta.Tuple[inj.Binding, ta.Any]] = dc.field(default_factory=list)

    def get_binding_manager_key(self, binding: inj.Binding) -> inj.Key[LifecycleManager]:
        return inj.Key(LifecycleManager)

    def __call__(self, injector: inj.Injector, key, fn):
        st = self.State(key)
        self._stack.append(st)
        try:
            instance = fn()
        finally:
            popped = self._stack.pop()
            check.state(popped is st)

        if isinstance(instance, Lifecycle) and not isinstance(instance, LifecycleManager):
            inst_binding = check.isinstance(injector.get_binding(key), inj.Binding)
            if self._stack:
                self._stack[-1].dependencies.append((inst_binding, instance))

            if instance not in self._seen:
                man_key = self.get_binding_manager_key(inst_binding)
                man: LifecycleManager = injector.get(man_key)
                deps = [o for b, o in st.dependencies]  # if b.scoping == binding.scoping]
                man.add(instance, deps)
                self._seen.add(instance)

        elif self._stack:
            self._stack[-1].dependencies.extend(st.dependencies)

        return instance
