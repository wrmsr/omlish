import pytest

from omcore.secrets.tests.harness import HarnessSecrets

from .....models.default import default_model_catalog
from .....types.context import Context
from .....types.messages import UserMessage
from .....types.models import ModelKey
from .....types.options import Options
from ..stream import OpenaiCompletionsStreamBackend


@pytest.mark.asyncs('asyncio')
@pytest.mark.online
async def test_openai_chat_stream_model_async(harness):
    model = (ModelKey('openai', 'gpt-5.4-mini'), 'openai_api_key')

    model_key, api_key_name = model

    svc = OpenaiCompletionsStreamBackend(
        default_model_catalog()[model_key],  # noqa
        api_key=harness[HarnessSecrets].get_or_skip(api_key_name),
    )

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
            print(e)
        print(it.result.must())

    print(await svc.immediate(ctx, opts))
