import dataclasses as dc
import typing as ta

from omlish import lang

from ..services import Service
from .chat import ChatService
from .chat import LocalChatServiceImpl
from .chat import RemoteChatServiceImpl


SelectorT_contra = ta.TypeVar('SelectorT_contra', contravariant=True)

ServiceT = ta.TypeVar('ServiceT', bound=Service)
ServiceT_co = ta.TypeVar('ServiceT_co', bound=Service, covariant=True)
ServiceU = ta.TypeVar('ServiceU', bound=Service)

##


class ServiceFactory(ta.Protocol[ServiceT_co]):
    def __call__(self, *args: ta.Any, **kwargs: ta.Any) -> ServiceT_co:
        ...


class SelectorServiceFactory(ta.Protocol[SelectorT_contra, ServiceT_co]):
    def __call__(
            self,
            __selector: SelectorT_contra,  # ? Mypy handles '__' param names differently?  # noqa
            *args: ta.Any,
            **kwargs: ta.Any,
    ) -> ServiceT_co:
        ...


def test_factory():
    def fn(name: str) -> ChatService:
        if name == 'local':
            return LocalChatServiceImpl()
        elif name == 'remote':
            return RemoteChatServiceImpl()
        else:
            raise ValueError(name)

    lang.static_check_isinstance[ServiceFactory](fn)
    lang.static_check_isinstance[ServiceFactory[Service]](fn)
    lang.static_check_isinstance[ServiceFactory[ChatService]](fn)
    sf: ServiceFactory[ChatService] = fn  # noqa
    assert isinstance(sf('local'), LocalChatServiceImpl)

    lang.static_check_isinstance[SelectorServiceFactory](fn)
    lang.static_check_isinstance[SelectorServiceFactory[str, Service]](fn)
    lang.static_check_isinstance[SelectorServiceFactory[str, ChatService]](fn)
    ssf: SelectorServiceFactory[str, ChatService] = fn  # noqa
    assert isinstance(ssf('local'), LocalChatServiceImpl)


##


def new_service_from_name(ty: type[ServiceT], name: str) -> ServiceT:
    if ty == ChatService:
        if name == 'local':
            return ta.cast(ServiceT, LocalChatServiceImpl())
        elif name == 'remote':
            return ta.cast(ServiceT, RemoteChatServiceImpl())
        else:
            raise ValueError(name)
    else:
        raise TypeError(ty)


def test_factory2():
    cs: ChatService = new_service_from_name(ChatService, 'local')  # type: ignore[type-abstract]
    assert isinstance(cs, LocalChatServiceImpl)


##


class TypedServiceFactory(ta.Generic[ServiceT]):
    @dc.dataclass(frozen=True)
    class _Bound(ta.Generic[ServiceU]):  # noqa
        cls: type[ServiceU]

        def new(self, name: str, *args: ta.Any, **kwargs: ta.Any) -> ServiceU:
            return new_service_from_name(self.cls, name, *args, **kwargs)

    def __class_getitem__(cls, *args, **kwargs):
        [bind_cls] = args
        return TypedServiceFactory._Bound(bind_cls)

    @classmethod
    def new(cls, name: str, *args: ta.Any, **kwargs: ta.Any) -> ServiceT:  # noqa
        raise TypeError


def test_factory3():
    cs: ChatService = TypedServiceFactory[ChatService].new('local')
    lang.static_check_isinstance[ChatService](cs)
    assert isinstance(cs, LocalChatServiceImpl)
