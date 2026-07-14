import pytest

from omcore.secrets.tests.harness import HarnessSecrets

from .....models.default import default_model_catalog
from .....types.context import Context
from .....types.messages import UserMessage
from .....types.models import ModelKey
from .....types.options import Options
from ..backend import AnthropicMessagesBackend


@pytest.mark.online
@pytest.mark.asyncs('asyncio')
@pytest.mark.parametrize('model', [
    (ModelKey('anthropic', 'claude-sonnet-5'), 'anthropic_api_key'),
])
@pytest.mark.parametrize('max_tokens', [None, 1024])
async def test_anthropic_backend(
        harness,
        model,
        max_tokens,
):
    model_key, api_key_name = model

    svc = AnthropicMessagesBackend(
        default_model_catalog()[model_key],  # noqa
        api_key=harness[HarnessSecrets].get_or_skip(api_key_name),
    )

    out = await svc.complete(
        Context(
            system_prompt='You are a helpful assistant.',
            messages=[
                UserMessage('hi'),
            ],
        ),
        Options(
            max_tokens=max_tokens,

        ),
    )

    print(out)
