import pytest

from omcore.secrets.tests.harness import HarnessSecrets

from .....models.default import default_model_catalog
from .....types.context import Context
from .....types.messages import AiMessage
from .....types.messages import UserMessage
from .....types.models import ModelKey
from .....types.options import Options
from ..stream import AnthropicMessagesStreamBackend


@pytest.mark.xfail
@pytest.mark.asyncs('asyncio')
@pytest.mark.online
async def test_anthropic_chat_stream_model_async(harness):
    model = (ModelKey('anthropic', 'claude-sonnet-5'), 'anthropic_api_key')

    model_key, api_key_name = model

    svc = AnthropicMessagesStreamBackend(
        default_model_catalog()[model_key],  # noqa
        api_key=harness[HarnessSecrets].get_or_skip(api_key_name),
    )

    #

    events: list = []

    async with (await svc.stream(
        ctx := Context(
            system_prompt='You are a helpful assistant.',
            messages=[
                UserMessage('hi'),
            ],
        ),
        opts := Options(
            max_tokens=None,
        ),
    )) as it:
        async for e in it:
            events.append(e)
        out = it.result.must()

    assert isinstance(out, AiMessage)

    #

    out = await svc.immediate(ctx, opts)

    assert isinstance(out, AiMessage)
