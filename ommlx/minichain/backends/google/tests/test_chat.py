from omlish.secrets.tests.harness import HarnessSecrets

from ....chat.messages import UserMessage
from ....generative import MaxTokens
from ....generative import Temperature
from ..chat import GoogleChatModel


def test_chat(harness):
    llm = GoogleChatModel(api_key=harness[HarnessSecrets].get_or_skip('gemini_api_key').reveal())

    resp = llm(
        [UserMessage('Is water dry?')],
        Temperature(.1),
        MaxTokens(64),
    )
    print(resp)
    assert resp.v
