from omlish.secrets.tests.harness import HarnessSecrets

from ...chat.messages import UserMessage
from ...chat.services import ChatRequest
from ...chat.services import ChatService
from ...registry import registry_new
from ...registry import registry_of
from ...services import ServiceFacade
from ...standard import ApiKey


def test_new_backend_openai(harness):
    llm: ChatService = registry_new(
        ChatService,  # type: ignore[type-abstract]
        'openai',
        ApiKey(harness[HarnessSecrets].get_or_skip('openai_api_key').reveal()),
    )

    resp = llm.invoke(ChatRequest([UserMessage('what is 2 + 2?')]))
    print(resp.v)


def test_new_backend_openai2(harness):
    llm = ServiceFacade(registry_of[ChatService].new(
        'openai',
        ApiKey(harness[HarnessSecrets].get_or_skip('openai_api_key').reveal()),
    ))

    resp = llm([UserMessage('what is 2 + 2?')])
    print(resp.v)
