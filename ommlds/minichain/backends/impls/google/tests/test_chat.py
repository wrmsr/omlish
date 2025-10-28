from omlish import lang
from omlish.http import all as http
from omlish.secrets.tests.harness import HarnessSecrets

from .....chat.messages import UserMessage
from .....services import Request
from .....standard import ApiKey
from ..chat import GoogleChatChoicesService


def test_chat(harness):
    llm = GoogleChatChoicesService(
        ApiKey(harness[HarnessSecrets].get_or_skip('gemini_api_key').reveal()),
        http_client=http.SyncAsyncHttpClient(http.client()),
    )

    resp = lang.sync_await(llm.invoke(Request(
        [UserMessage('Is water dry?')],
        # Temperature(.1),
        # MaxTokens(64),
    )))
    print(resp)
    assert resp.v
