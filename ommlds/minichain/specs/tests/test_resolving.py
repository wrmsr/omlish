from omlish import lang

from ...chat.choices.services import ChatChoicesService
from ..instantiate import instantiate_backend_spec
from ..resolving import DEFAULT_BACKEND_SPEC_RESOLVER
from ..types import BackendSpec
from ..types import ConfigBackendSpec
from ..types import ModelBackendSpec
from ..types import NameBackendSpec
from ..types import RetryBackendSpec


def test_resolving():
    bsr = DEFAULT_BACKEND_SPEC_RESOLVER

    for _ in range(2):
        for bs in [
            NameBackendSpec('openai'),
            BackendSpec.of('openai'),
            BackendSpec.of("{model: 'gpt'}"),
            ConfigBackendSpec(ModelBackendSpec('gpt'), [{'api_key': 'foo'}]),
            RetryBackendSpec(ConfigBackendSpec(ModelBackendSpec('gpt'), [{'api_key': 'foo'}])),
            BackendSpec.of("{config: {child: {name: 'ollama'}, configs: [{model_name: 'qwen3.6:35b-a3b-mlx-bf16'}]}}"),
            BackendSpec.of("{config: {child: {name: ollama}, configs: [{model_name: 'qwen3.6:35b-a3b-mlx-bf16'}]}}"),
        ]:
            rbs = bsr.resolve(ChatChoicesService, bs)
            print(rbs)

            svc = lang.sync_await(instantiate_backend_spec(rbs))
            print(svc)

            print()
