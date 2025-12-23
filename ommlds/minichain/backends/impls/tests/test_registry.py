import pytest

from omlish import lang
from omlish.http import all as http
from omlish.secrets.tests.harness import HarnessSecrets

from ....chat.choices.services import ChatChoicesRequest
from ....chat.choices.services import ChatChoicesService
from ....chat.messages import UserMessage
from ....registries.globals import registry_new
from ....registries.globals import registry_of
from ....services import ServiceFacade
from ....standard import ApiKey


@pytest.mark.online
def test_new_backend_openai(harness):
    llm: ChatChoicesService = registry_new(
        ChatChoicesService,
        'openai',
        ApiKey(harness[HarnessSecrets].get_or_skip('openai_api_key').reveal()),
        http_client=http.SyncAsyncHttpClient(http.client()),
    )

    resp = lang.sync_await(llm.invoke(ChatChoicesRequest([UserMessage('what is 2 + 2?')])))
    print(resp.v)


@pytest.mark.online
def test_new_backend_openai2(harness):
    llm = ServiceFacade(registry_of[ChatChoicesService].new(
        'openai',
        ApiKey(harness[HarnessSecrets].get_or_skip('openai_api_key').reveal()),
        http_client=http.SyncAsyncHttpClient(http.client()),
    ))

    resp = lang.sync_await(llm([UserMessage('what is 2 + 2?')]))
    print(resp.v)
