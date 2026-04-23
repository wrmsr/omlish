from ....chat.choices.services import ChatChoicesService
from ..resolving import DEFAULT_BACKEND_SPEC_RESOLVER
from ..types import ModelBackendSpec
from ..types import NameBackendSpec
from ..types import RetryBackendSpec


def test_strings():
    bsr = DEFAULT_BACKEND_SPEC_RESOLVER

    for _ in range(2):
        print(bsr.resolve(ChatChoicesService, NameBackendSpec('openai')))
        print(bsr.resolve(ChatChoicesService, ModelBackendSpec('gpt', [{'api_key': 'foo'}])))
        print(bsr.resolve(ChatChoicesService, RetryBackendSpec(ModelBackendSpec('gpt', [{'api_key': 'foo'}]))))
