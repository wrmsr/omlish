import abc
import typing as ta

from .. import check
from .. import dataclasses as dc
from .. import dynamic as dyn
from .. import lang
from .. import properties


T = ta.TypeVar('T')
K = ta.TypeVar('K')
V = ta.TypeVar('V')
ElementT = ta.TypeVar('ElementT', bound='Element')
BindingT = ta.TypeVar('BindingT', bound='Binding')


class MISSING(lang.Marker):
    pass


class Element(lang.Abstract):

    def possess(self: ElementT, injector: 'Injector') -> ElementT:  # noqa
        return self


class Key(dc.Pure, ta.Generic[T], unsafe_hash=True):
    type: ta.Type[T]
    annotation: ta.Any = None

    def __post_init__(self) -> None:
        hash(self)


class RequiredKey(dc.Pure, Element, ta.Generic[T]):
    key: Key[T]
    required_by: ta.Any


class Provider(lang.Abstract, ta.Generic[T]):

    @lang.abstract
    def __call__(self) -> T:
        raise NotImplementedError


class BindingSource(lang.Abstract):
    EXPLICIT: 'BindingSource'
    PROVIDER: 'BindingSource'
    INTERNAL: 'BindingSource'
    EXPOSED_PRIVATE: 'BindingSource'


def _special_binding_source(name: str) -> BindingSource:
    return lang.new_type(name + 'BindingSource', (BindingSource,), {})()


BindingSource.EXPLICIT = _special_binding_source('Explicit')
BindingSource.PROVIDER = _special_binding_source('Provider')
BindingSource.INTERNAL = _special_binding_source('Internal')
BindingSource.EXPOSED_PRIVATE = _special_binding_source('ExposedPrivate')


class JitBindingSource(dc.Pure, BindingSource):
    required_by: ta.Any


class Binding(dc.Frozen, Element, ta.Generic[T], reorder=True):
    key: Key[T]
    provider: Provider[T]
    scoping: ta.Type['Scope']
    source: BindingSource

    _injector: ta.Optional['Injector'] = dc.field(None, kwonly=True)

    def __post_init__(self) -> None:
        check.isinstance(self.scoping, type)

    def possess(self: BindingT, injector: 'Injector') -> BindingT:
        check.none(self._injector)
        return dc.replace(self, _injector=check.isinstance(injector, Injector))

    def provide(self) -> T:
        with Injector._CURRENT(check.not_none(self._injector)):
            return self._injector._scopes[self.scoping].provide(self)


class Scope(lang.Abstract):

    @lang.abstract
    def provide(self, binding: Binding[T]) -> T:
        raise NotImplementedError


class ScopeBinding(dc.Pure, Element):
    scoping: ta.Type[Scope]


ProvisionListener = ta.Callable[['Injector', ta.Union[Key, ta.Any], ta.Callable[[], ta.Any]], None]


class ProvisionListenerBinding(dc.Pure, Element):
    listener: ProvisionListener


class MultiBinding(Binding[T], lang.Abstract):
    pass


class MultiProvider(Provider[T], lang.Abstract):
    pass


class PrivateElements(dc.Pure, Element):
    elements: ta.List[Element]


class ExposedKey(dc.Pure, Element, ta.Generic[T]):
    key: Key[T]


class InjectionError(Exception):
    pass


class InjectionKeyError(dc.Frozen, InjectionError):
    key: Key


class InjectionRequiredKeyError(InjectionKeyError):
    required_by: ta.Any = None


class InjectionBlacklistedKeyError(InjectionKeyError):
    pass


class InjectionOpaqueError(dc.Frozen, InjectionError):
    params: ta.Sequence[str]


class InjectionRecursionException(dc.Frozen, InjectionError):
    key: Key[T]


Source = ta.Union['PrivateBinder', 'Binder', ta.Iterable[Element]]


class InjectorConfig(dc.Pure):
    enable_jit_bindings: bool = dc.field(False, kwonly=True)
    fail_early: bool = dc.field(False, kwonly=True)
    lock: lang.DefaultLockable = dc.field(None, kwonly=True)
    weak_children: bool = dc.field(False, kwonly=True)
    enable_cyclic_proxies: bool = dc.field(False, kwonly=True)


class Injector(lang.Abstract):

    _CURRENT: dyn.Var['Injector'] = dyn.Var()

    @properties.class_
    @classmethod
    def current(cls) -> 'Injector':
        return check.isinstance(cls._CURRENT(), cls)

    @abc.abstractproperty
    def config(self) -> InjectorConfig:
        raise NotImplementedError

    @abc.abstractproperty
    def parent(self) -> 'ta.Optional[Injector]':
        raise NotImplementedError

    @abc.abstractmethod
    def create_child(self, *sources: Source) -> 'Injector':
        raise NotImplementedError

    @abc.abstractmethod
    def get_binding(
            self,
            target: ta.Union[Key[T], ta.Type[T]],
            *,
            has_default: bool = False,
    ) -> ta.Optional[Binding[T]]:
        raise NotImplementedError

    @abc.abstractmethod
    def get(
            self,
            target: ta.Union[Key[T], ta.Type[T]],
            default: ta.Any = MISSING,
    ) -> T:
        raise NotImplementedError

    def __getitem__(
            self,
            target: ta.Union[Key[T], ta.Type[T]],
    ) -> T:
        return self.get(target)

    @abc.abstractmethod
    def get_elements_by_type(
            self,
            cls: ta.Type[Element],
            *,
            parent: bool = False,
            children: bool = False,
    ) -> ta.List[Element]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_bindings(
            self,
            key: Key[MultiBinding[T]],
            *,
            parent: bool = False,
            children: bool = False,
    ) -> ta.List[Binding]:
        raise NotImplementedError


class Binder(lang.Abstract):

    @abc.abstractproperty
    def elements(self) -> ta.Sequence[Element]:
        raise NotImplementedError

    @abc.abstractmethod
    def bind(
            self,
            target: ta.Union[Key, ta.Type, ta.Any],
            *,
            annotated_with: ta.Any = MISSING,

            to: ta.Union[Key, ta.Type] = MISSING,
            to_provider: ta.Union[Key, ta.Type] = MISSING,
            to_instance: ta.Any = MISSING,

            as_singleton: bool = MISSING,
            as_eager_singleton: bool = MISSING,
            in_: ta.Union[ta.Type[Scope], ta.Type[MISSING]] = MISSING,

            source: BindingSource = BindingSource.EXPLICIT,

            binding_factory: ta.Callable[..., Binding] = Binding,
    ) -> Binding:
        raise NotImplementedError

    @abc.abstractmethod
    def bind_callable(
            self,
            callable: ta.Callable[..., T],
            *,
            key: Key[T] = None,
            annotated_with: ta.Any = MISSING,

            kwargs: ta.Mapping[str, ta.Union[Key, ta.Type]] = None,
            assists: ta.AbstractSet[str] = None,

            as_singleton: bool = MISSING,
            as_eager_singleton: bool = MISSING,
            in_: ta.Union[ta.Type[Scope], ta.Type[MISSING]] = MISSING,

            source: BindingSource = BindingSource.EXPLICIT,
    ) -> Binding:
        raise NotImplementedError

    @abc.abstractmethod
    def bind_class(
            self,
            cls: ta.Type[T],
            *,
            key: Key[T] = None,

            assists: ta.AbstractSet[str] = None,

            as_singleton: bool = MISSING,
            as_eager_singleton: bool = MISSING,
            in_: ta.Union[ta.Type[Scope], ta.Type[MISSING]] = MISSING,

            source: BindingSource = BindingSource.EXPLICIT,
    ) -> Binding:
        raise NotImplementedError

    class _Child(lang.Abstract):

        def __init__(self, binder: 'Binder') -> None:
            super().__init__()

            self._binder = binder

    class SetBinder(_Child, ta.Generic[T], lang.Abstract):

        @abc.abstractmethod
        def bind(
                self,
                *,
                to: ta.Union[Key, ta.Type] = MISSING,
                to_provider: ta.Union[Key, ta.Type] = MISSING,
                to_instance: ta.Any = MISSING,

                as_singleton: bool = MISSING,
                as_eager_singleton: bool = MISSING,
                in_: ta.Union[ta.Type[Scope], ta.Type[MISSING]] = MISSING,

                source: BindingSource = BindingSource.EXPLICIT,
        ) -> Binding:
            raise NotImplementedError

    @abc.abstractmethod
    def new_set_binder(
            self,
            value: ta.Type,
            *,
            annotated_with: ta.Any = None,

            as_singleton: bool = MISSING,
            as_eager_singleton: bool = MISSING,
            in_: ta.Union[ta.Type[Scope], ta.Type[MISSING]] = MISSING,

            source: BindingSource = BindingSource.EXPLICIT,
    ) -> SetBinder:
        raise NotImplementedError

    class DictBinder(_Child, ta.Generic[K, V], lang.Abstract):

        @abc.abstractmethod
        def bind(
                self,
                assignment: K,
                *,
                to: ta.Union[Key, ta.Type] = MISSING,
                to_provider: ta.Union[Key, ta.Type] = MISSING,
                to_instance: ta.Any = MISSING,

                as_singleton: bool = MISSING,
                as_eager_singleton: bool = MISSING,
                in_: ta.Union[ta.Type[Scope], ta.Type[MISSING]] = MISSING,

                source: BindingSource = BindingSource.EXPLICIT,
        ) -> Binding:
            raise NotImplementedError

    @abc.abstractmethod
    def new_dict_binder(
            self,
            key: ta.Type,
            value: ta.Type,
            *,
            annotated_with: ta.Any = None,

            as_singleton: bool = MISSING,
            as_eager_singleton: bool = MISSING,
            in_: ta.Union[ta.Type[Scope], ta.Type[MISSING]] = MISSING,

            source: BindingSource = BindingSource.EXPLICIT,
    ) -> DictBinder:
        raise NotImplementedError

    @abc.abstractmethod
    def bind_scope(
            self,
            scoping: ta.Type[Scope],
    ) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def bind_provision_listener(
            self,
            target: ProvisionListener,
    ) -> None:
        raise NotImplementedError


class PrivateBinder(Binder, lang.Abstract):

    @abc.abstractmethod
    def expose(
            self,
            target: ta.Union[Key, ta.Type, ta.Any],
            *,
            annotated_with: ta.Any = MISSING,
    ) -> None:
        raise NotImplementedError
