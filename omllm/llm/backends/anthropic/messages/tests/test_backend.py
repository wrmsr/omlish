import pytest

from omcore.secrets.tests.harness import HarnessSecrets

from .....models.default import default_model_catalog
from .....types.context import Context
from .....types.messages import UserMessage
from .....types.models import ModelKey
from ..backend import AnthropicMessagesBackend


@pytest.mark.online
@pytest.mark.asyncs('asyncio')
async def test_anthropic_backend(harness):
    svc = AnthropicMessagesBackend(
        default_model_catalog()[ModelKey('anthropic', 'claude-sonnet-5')],
        api_key=harness[HarnessSecrets].get_or_skip('anthropic_api_key'),
    )

    out = await svc.complete(Context(
        system_prompt='You are a helpful assistant.',
        messages=[
            UserMessage('hi'),
        ],
    ))

    print(out)
