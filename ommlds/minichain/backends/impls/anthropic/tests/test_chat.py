import pytest

from omlish import lang
from omlish import marshal as msh
from omlish.http import all as http
from omlish.secrets.tests.harness import HarnessSecrets

from .....chat.choices.services import ChatChoicesRequest
from .....chat.messages import UserMessage
from .....llms.types import Temperature
from .....standard import ApiKey
from ..chat import AnthropicChatChoicesService


@pytest.mark.online
def test_anthropic(harness):
    llm = AnthropicChatChoicesService(
        ApiKey(harness[HarnessSecrets].get_or_skip('anthropic_api_key').reveal()),
        http_client=http.SyncAsyncHttpClient(http.client()),
    )

    req = ChatChoicesRequest(
        [UserMessage('Is water dry?')],
        [Temperature(.1)],
    )

    rm = msh.marshal(req)
    print(rm)
    req2 = msh.unmarshal(rm, ChatChoicesRequest)
    print(req2)

    resp = lang.sync_await(llm.invoke(req))
    print(resp)
    assert resp.v
