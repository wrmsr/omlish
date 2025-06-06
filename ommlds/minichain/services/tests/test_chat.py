import typing as ta

import pytest

from omlish import lang

from .._typedvalues import _TypedValuesTypeError  # noqa
from ..requests import Request
from .chat import ApiKey
from .chat import ChatRequest
from .chat import ChatResponse
from .chat import ChatService
from .chat import LocalChatRequest
from .chat import LocalChatResponse  # noqa
from .chat import LocalChatService
from .chat import LocalChatServiceImpl
from .chat import MaxTokens
from .chat import Message
from .chat import ModelPath
from .chat import RemoteChatRequest
from .chat import RemoteChatResponse  # noqa
from .chat import RemoteChatService
from .chat import RemoteChatServiceImpl


##


def test_impl_mros():  # noqa
    class FooLcs:  # noqa
        def invoke(self, request: LocalChatRequest) -> LocalChatResponse:
            raise NotImplementedError

    lang.static_check_issubclass[ChatService](FooLcs)
    lang.static_check_issubclass[LocalChatService](FooLcs)

    lcs: LocalChatService = FooLcs()  # noqa
    cs: ChatService = FooLcs()

    class BarLcs:  # noqa
        def invoke(self, request: LocalChatRequest) -> LocalChatResponse:
            raise NotImplementedError

    lang.static_check_issubclass[ChatService](BarLcs)
    lang.static_check_issubclass[LocalChatService](BarLcs)

    lcs = BarLcs()  # noqa
    cs = FooLcs()  # noqa

    class FooCs:
        def invoke(self, request: ChatRequest) -> ChatResponse:
            raise NotImplementedError

    lang.static_check_issubclass[ChatService](FooCs)

    # lcs = FooCs()  # ❌
    cs = FooCs()  # noqa


def test_mypy():
    # (a) Should type-check: handing a ChatRequest to a LocalChatService

    chat_request: ChatRequest = Request([Message('user', 'hi')], [MaxTokens(10)])
    chat_request2 = ChatRequest([Message('user', 'hi')], [MaxTokens(10)])

    local_chat_service: LocalChatService = LocalChatServiceImpl()
    local_chat_service.invoke(chat_request)  # OK
    local_chat_service.invoke(chat_request2)  # OK

    # (b) Still type-checks when you pass LocalChatRequest

    local_chat_request: LocalChatRequest = Request([Message('user', 'hi')], [MaxTokens(10), ModelPath('my_model')])
    local_chat_request2 = LocalChatRequest([Message('user', 'hi')], [MaxTokens(10), ModelPath('my_model')])
    local_chat_service.invoke(local_chat_request)  # OK
    local_chat_service.invoke(local_chat_request2)  # OK

    # (c) The result LocalChatResponse can be assigned to ChatResponse

    local_chat_response_as_chat_response: ChatResponse = local_chat_service.invoke(local_chat_request)  # OK  # noqa

    # (d) Remote side: also works with ChatService

    remote_chat_service: RemoteChatService = RemoteChatServiceImpl()
    remote_chat_service.invoke(chat_request)  # OK

    remote_chat_request: RemoteChatRequest = Request([Message('user', 'hi')], [MaxTokens(10), ApiKey('secret')])
    remote_chat_request2 = RemoteChatRequest([Message('user', 'hi')], [MaxTokens(10), ApiKey('secret')])
    remote_chat_service.invoke(remote_chat_request)  # OK
    remote_chat_service.invoke(remote_chat_request2)  # OK

    remote_chat_response_as_chat_response: ChatResponse = remote_chat_service.invoke(remote_chat_request)  # OK  # noqa

    # (e) These should all fail mypy:

    #  1) Cannot give RemoteRequest to LocalChatService
    # local_chat_service.invoke(remote_chat_request)  # ❌

    #  2) Cannot treat LocalChatResponse as RemoteChatResponse
    # local_chat_response_as_remote: RemoteChatResponse = local_chat_service.invoke(local_chat_request)  # ❌

    #  3) Cannot give LocalChatRequest to RemoteChatService
    # remote_chat_service.invoke(local_chat_request)  # ❌

    #  4) Cannot treat RemoteChatResponse as LocalChatResponse
    # remote_chat_response_as_local: LocalChatResponse = remote_chat_service.invoke(remote_chat_request)  # ❌

    #  5) Cannot use wrong options
    # local_chat_request_with_remote_option = LocalChatRequest([Message('user', 'hi')], [MaxTokens(10), ApiKey('secret')])  # noqa
    # local_chat_request_with_remote_option2: LocalChatRequest = ChatRequest([Message('user', 'hi')], [MaxTokens(10), ApiKey('secret')])  # noqa


def test_reflect():
    args: tuple[ta.Any, ...] = ([Message('user', 'hi')], [MaxTokens(10)])
    for _ in range(2):
        chat_request = ChatRequest(*args)
        # print(chat_request.type_args)
        print(chat_request)


# def test_new():
#     args: tuple[ta.Any, ...] = ([Message('user', 'hi')], MaxTokens(10))
#     print(ChatRequest.new(*args))
#     ta.reveal_type(ChatRequest.new)


def test_check_tvs():
    lcr = LocalChatRequest([Message('user', 'hi')], [ModelPath('my_model'), MaxTokens(10)])
    lcr.validate()

    lcr = LocalChatRequest([Message('user', 'hi')], [ApiKey('secret'), MaxTokens(10)])  # type: ignore[list-item]
    with pytest.raises(_TypedValuesTypeError):
        lcr.validate()


def test_orig_class_abuse():
    lcr = LocalChatRequest([Message('user', 'hi')], [MaxTokens(10), ModelPath('my_model')])
    print(lcr)
    cr = ChatRequest(lcr)  # type: ignore[arg-type]
    print(cr)
