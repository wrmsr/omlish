from omlish import lang
from omlish.secrets.tests.harness import HarnessSecrets

from ....chat.messages import UserMessage
from ....services import Request
from ..mistral import MistralChatChoicesService
from ..mistral import TooManyRequestsMistralError


def test_mistral_chat(harness):
    key = harness[HarnessSecrets].get_or_skip('mistral_api_key')
    svc = MistralChatChoicesService(api_key=key.reveal())
    try:
        resp = lang.sync_await(svc.invoke(Request([UserMessage('hi')])))
    except TooManyRequestsMistralError:
        pass
    else:
        print(resp.v)
