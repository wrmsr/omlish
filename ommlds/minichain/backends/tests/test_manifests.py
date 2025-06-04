from omlish.secrets.tests.harness import HarnessSecrets

from ...chat.messages import UserMessage
from ...chat.services import ChatRequest
from ...chat.services import ChatService
from ...services import Service
from ...standard import ApiKey
from ..manifests import backend_of
from ..manifests import new_backend


def test_new_backend_openai(harness):
    llm: ChatService = new_backend(
        ChatService,  # type: ignore[type-abstract]
        'openai',
        ApiKey(harness[HarnessSecrets].get_or_skip('openai_api_key').reveal()),
    )

    resp = llm.invoke(ChatRequest([UserMessage('what is 2 + 2?')]))
    print(resp.v)


def test_new_backend_openai2(harness):
    llm = backend_of[ChatService].new(
        'openai',
        ApiKey(harness[HarnessSecrets].get_or_skip('openai_api_key').reveal()),
    )

    # assert isinstance(llm, ChatService)
    assert isinstance(llm, Service)
