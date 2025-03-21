from omlish.secrets.tests.harness import HarnessSecrets

from ...chat.messages import UserMessage
from ...chat.models import ChatModel
from ..manifests import new_backend


def test_new_backend_openai(harness):
    llm = new_backend(
        ChatModel,  # type: ignore[type-abstract]
        'openai',
        api_key=harness[HarnessSecrets].get_or_skip('openai_api_key').reveal(),
    )

    resp = llm(UserMessage('what is 2 + 2?'))
    print(resp)
