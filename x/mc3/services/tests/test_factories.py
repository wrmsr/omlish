import typing as ta

from omlish import lang

from ..services import Service
from .chat import ChatService
from .chat import LocalChatServiceImpl
from .chat import RemoteChatServiceImpl


SelectorT_contra = ta.TypeVar('SelectorT_contra', contravariant=True)

ServiceT_co = ta.TypeVar('ServiceT_co', bound=Service, covariant=True)


##


class ServiceFactory(ta.Protocol[ServiceT_co]):
    def __call__(self, *args: ta.Any, **kwargs: ta.Any) -> ServiceT_co:
        ...


class SelectorServiceFactory(ta.Protocol[SelectorT_contra, ServiceT_co]):
    def __call__(self, selector: SelectorT_contra, *args: ta.Any, **kwargs: ta.Any) -> ServiceT_co:
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

    sf: ServiceFactory[ChatService] = fn  # noqa

    assert isinstance(sf('local'), LocalChatServiceImpl)
