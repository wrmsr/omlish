from omlish.secrets.tests.harness import HarnessSecrets

from ...chat.messages import UserMessage
from ...services import Request
from ..mistral import MistralChatChoicesService


def test_mistral_chat(harness):
    key = harness[HarnessSecrets].get_or_skip('mistral_api_key')
    svc = MistralChatChoicesService(api_key=key.reveal())
    resp = svc.invoke(Request([UserMessage('hi')]))
    print(resp.v)
