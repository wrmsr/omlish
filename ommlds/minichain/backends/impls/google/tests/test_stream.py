from omlish import lang
from omlish.http import all as http
from omlish.secrets.tests.harness import HarnessSecrets

from .....chat.messages import UserMessage
from .....chat.stream.services import ChatChoicesStreamRequest
from .....standard import ApiKey
from ..stream import GoogleChatChoicesStreamService


def test_google_chat_stream_model(harness):
    llm = GoogleChatChoicesStreamService(
        ApiKey(harness[HarnessSecrets].get_or_skip('gemini_api_key').reveal()),
        http_client=http.SyncAsyncHttpClient(http.client()),
    )

    foo_req: ChatChoicesStreamRequest
    for foo_req in [
        ChatChoicesStreamRequest([UserMessage('Is water dry?')]),
        ChatChoicesStreamRequest([UserMessage('Is air wet?')]),
    ]:
        print(foo_req)

        with lang.sync_async_with(lang.sync_await(llm.invoke(foo_req)).v) as it:
            for o in lang.sync_aiter(it):
                print(o)
            print(it.outputs)
