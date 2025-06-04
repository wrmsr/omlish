from ..facades import ServiceFacade
from ..requests import Request
from .chat import ApiKey
from .chat import Chat
from .chat import ChatRequest
from .chat import ChatResponse
from .chat import LocalChatRequest
from .chat import LocalChatRequestOption
from .chat import LocalChatResponse  # noqa
from .chat import LocalChatResponseOutput
from .chat import LocalChatService  # noqa
from .chat import LocalChatServiceImpl
from .chat import MaxTokens
from .chat import Message
from .chat import ModelPath
from .chat import RemoteChatRequest
from .chat import RemoteChatResponse  # noqa


def test_facade():
    local_chat_service_impl = LocalChatServiceImpl()
    # ta.reveal_type(local_chat_service_impl)

    local_chat_service = ServiceFacade(local_chat_service_impl)
    # ta.reveal_type(local_chat_service)

    print(local_chat_service([Message('user', 'hi')], MaxTokens(10)))
    # print(local_chat_service([Message('user', 'hi')], ApiKey('secret')))  # ❌

    local_chat_service2 = ServiceFacade[
        Chat,
        LocalChatRequestOption,
        Message,
        LocalChatResponseOutput,
    ](local_chat_service_impl)
    # ta.reveal_type(local_chat_service2)

    print(local_chat_service2([Message('user', 'hi')], MaxTokens(10)))
    # print(local_chat_service2([Message('user', 'hi')], ApiKey('secret')))  # ❌


def test_facade_types():
    local_chat_service = ServiceFacade(LocalChatServiceImpl())
    # ta.reveal_type(local_chat_service)

    chat_request: ChatRequest = Request([Message('user', 'hi')], [MaxTokens(10)])
    chat_request2 = ChatRequest([Message('user', 'hi')], [MaxTokens(10)])

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

    remote_chat_request: RemoteChatRequest = Request([Message('user', 'hi')], [MaxTokens(10), ApiKey('secret')])  # noqa
    remote_chat_request2 = RemoteChatRequest([Message('user', 'hi')], [MaxTokens(10), ApiKey('secret')])  # noqa

    # (e) These should all fail mypy:

    #  1) Cannot give RemoteRequest to LocalChatService
    # local_chat_service.invoke(remote_chat_request)  # ❌

    #  2) Cannot treat LocalChatResponse as RemoteChatResponse
    # local_chat_response_as_remote: RemoteChatResponse = local_chat_service.invoke(local_chat_request)  # ❌

    #  3) Cannot give LocalChatRequest to RemoteChatService
    # remote_chat_service.invoke(local_chat_request)  # ❌
