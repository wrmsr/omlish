import pytest

from omcore.secrets.tests.harness import HarnessSecrets

from ... import llm
from ..loop import Loop
from ..types import Context


@pytest.mark.asyncs('asyncio')
@pytest.mark.online
async def test_loop(harness):
    model = (llm.ModelKey('openai', 'gpt-5.4-mini'), 'openai_api_key')

    model_key, api_key_name = model

    svc = llm.OpenaiCompletionsStreamBackend(
        llm.default_model_catalog()[model_key],  # noqa
        api_key=harness[HarnessSecrets].get_or_skip(api_key_name),
    )

    loop = Loop(
        llm_backend=svc,
        context=Context(
            messages=[
                llm.UserMessage('Hi there!'),
            ],
        ),
    )

    loop_res = await loop.run()

    print(loop_res)
