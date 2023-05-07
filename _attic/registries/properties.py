import typing as ta
import weakref

from .. import check
from .. import lang
from .. import properties
from .composites import CompositeMultiRegistry
from .composites import CompositeRegistry
from .dicts import DictMultiRegistry
from .dicts import DictRegistry
from .types import Registry


K = ta.TypeVar('K')
V = ta.TypeVar('V')


class Property(properties.Property[Registry[K, V]]):

    def __init__(
            self,
            *,
            bind: ta.Optional[bool] = None,
            lock: lang.DefaultLockable = None,
            policy: ta.Optional[CompositeRegistry.Policy] = None,
    ) -> None:
        super().__init__()

        if policy is None:
            policy = CompositeRegistry.FIRST_ONE

        self._bind = bind
        self._lock = lang.default_lock(lock, True)
        self._policy = check.callable(policy)

        self._name: ta.Optional[str] = None
        self._registrations_attr_name = '__%s_%x_registrations' % (type(self).__name__, id(self))

        self._immediate_registries_by_cls: ta.MutableMapping[ta.Type, Registry[K, V]] = weakref.WeakKeyDictionary()  # noqa
        self._registries_by_tcls_by_scls: ta.MutableMapping[ta.Type, ta.MutableMapping[ta.Type, Registry[K, V]]] = weakref.WeakKeyDictionary()  # noqa

    def __set_name__(self, owner, name):
        if self._name is None:
            self._name = check.not_empty(name)
        else:
            check.state(self._name == name)

    class Registrations:

        def __init__(self) -> None:
            super().__init__()

            self._consumed = False
            self._key_sets_by_value = {}

    def _build_immediate_registry(self, items: ta.Iterable[ta.Tuple[K, V]]) -> DictRegistry[K, V]:
        return DictRegistry(items)

    def _get_immediate_registry(self, cls: ta.Type) -> Registry[K, V]:
        try:
            return self._immediate_registries_by_cls[cls]

        except KeyError:
            items = []

            registrations: Property.Registrations
            try:
                registrations = cls.__dict__[self._registrations_attr_name]
            except KeyError:
                pass

            else:
                check.isinstance(registrations, Property.Registrations)
                check.state(not registrations._consumed)

                for value, keys in registrations._key_sets_by_value.items():
                    for key in keys:
                        items.append((key, value))

                registrations._consumed = True

            registry = self._build_immediate_registry(items)
            registry.freeze()

            self._immediate_registries_by_cls[cls] = registry
            return registry

    def _build_composite_registry(self, regs: ta.Iterable[Registry[K, V]]) -> Registry[K, V]:
        return CompositeRegistry(regs, policy=self._policy)

    def get_registry(self, scls: ta.Type, tcls: ta.Type = None) -> Registry[K, V]:
        if tcls is None:
            tcls = scls

        try:
            return self._registries_by_tcls_by_scls[scls][tcls]
        except KeyError:
            pass

        with self._lock():
            try:
                tdct = self._registries_by_tcls_by_scls[scls]
            except KeyError:
                tdct = self._registries_by_tcls_by_scls[scls] = weakref.WeakKeyDictionary()

            try:
                return tdct[tcls]

            except KeyError:
                mro_registries = []
                adding = False
                for mcls in scls.__mro__:
                    if mcls is tcls:
                        adding = True
                    if adding:
                        mro_registries.append(self._get_immediate_registry(mcls))

                registry = self._build_composite_registry(mro_registries)

                tdct[tcls] = registry
                return registry

    class Accessor(ta.Mapping[K, V]):

        def __init__(self, owner, obj, cls, tcls=None):
            super().__init__()

            self._owner = owner
            self._obj = obj
            self._cls = cls
            self._tcls = tcls

        _registry: Registry[K, V] = None

        @property
        def registry(self) -> Registry[K, V]:
            if self._registry is None:
                self._registry = self._owner.get_registry(self._cls, self._tcls)
            return self._registry

        def __getitem__(self, key):
            ret = self.registry[key]

            if self._owner._bind:
                ret = ret.__get__(self._obj, self._cls)

            return ret

        def __iter__(self):
            return iter(self.registry)

        def __len__(self):
            return len(self.registry)

        _register = None

        @property
        def register(self):
            if self._register is None:
                self._register = self._owner.register
            return self._register

        _registering = None

        @property
        def registering(self):
            if self._registering is None:
                self._registering = self._owner.registering
            return self._registering

    def __get__(self, obj, cls=None, tcls=None) -> Accessor[K, V]:
        if cls is None:
            return self

        accessor = self.Accessor(self, obj, cls, tcls)

        if obj is not None and self._name is not None:
            obj.__dict__[check.not_empty(self._name)] = accessor

        return accessor

    def _register(self, cls_dct, value, keys):
        with self._lock():
            registrations: Property.Registrations
            try:
                registrations = cls_dct[self._registrations_attr_name]
            except KeyError:
                registrations = cls_dct[self._registrations_attr_name] = Property.Registrations()

            check.isinstance(registrations, Property.Registrations)
            check.state(not registrations._consumed)

            try:
                key_set = registrations._key_sets_by_value[value]
            except KeyError:
                key_set = registrations._key_sets_by_value[value] = set()

            key_set.update(keys)

    @lang.cls_dct_fn()
    def register(self, cls_dct, value, keys):
        self._register(cls_dct, value, keys)
        return value

    @lang.cls_dct_fn()
    def registering(self, cls_dct, *keys):
        def inner(value):
            self._register(cls_dct, value, keys)
            return value
        return inner


def property_(
        *,
        bind: ta.Optional[bool] = None,
        lock: lang.DefaultLockable = None,
        policy: ta.Optional[CompositeRegistry.Policy] = None,
) -> Property:
    return Property(
        bind=bind,
        lock=lock,
        policy=policy,
    )


# FIXME: class MultiProperty(Property[MultiRegistry[K, V]], Property[K, ta.AbstractSet[V]]):
class MultiProperty(Property):

    def __init__(
            self,
            *,
            bind: ta.Optional[bool] = None,
            lock: lang.DefaultLockable = None,
            policy: ta.Optional[CompositeRegistry.Policy] = None,
    ) -> None:
        if policy is None:
            policy = CompositeMultiRegistry.MERGE
        super().__init__(bind=bind, lock=lock, policy=policy)

    def _build_immediate_registry(self, items: ta.Iterable[ta.Tuple[K, V]]) -> DictMultiRegistry[K, V]:
        dct = {}
        for k, v in items:
            dct.setdefault(k, set()).add(v)
        return DictMultiRegistry(dct)

    def _build_composite_registry(self, regs: ta.Iterable[Registry[K, V]]) -> Registry[K, V]:
        return CompositeMultiRegistry(regs, policy=self._policy)


def multi_property(
        *,
        bind: ta.Optional[bool] = None,
        lock: lang.DefaultLockable = None,
        policy: ta.Optional[CompositeRegistry.Policy] = None,
) -> Property:
    return MultiProperty(
        bind=bind,
        lock=lock,
        policy=policy,
    )
