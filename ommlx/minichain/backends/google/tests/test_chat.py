from omlish.secrets.tests.harness import HarnessSecrets

from ....chat.messages import UserMessage
from ..chat import GoogleChatService


def test_chat(harness):
    llm = GoogleChatService(api_key=harness[HarnessSecrets].get_or_skip('gemini_api_key').reveal())

    resp = llm(
        [UserMessage('Is water dry?')],
        # Temperature(.1),
        # MaxTokens(64),
    )
    print(resp)
    assert resp.choices
