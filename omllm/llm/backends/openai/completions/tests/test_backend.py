import pytest

from omcore.secrets.tests.harness import HarnessSecrets

from .....models.default import default_model_catalog
from .....types.context import Context
from .....types.messages import UserMessage
from ..backend import OpenaiCompletionsBackend


@pytest.mark.asyncs('asyncio')
async def test_backend(harness):
    svc = OpenaiCompletionsBackend(
        default_model_catalog()['gpt-5.4-mini'],
        api_key=harness[HarnessSecrets].get_or_skip('openai_api_key'),
    )

    out = await svc.complete(Context(
        system_prompt='You are a helpful assistant.',
        messages=[
            UserMessage('hi'),
        ],
    ))

    print(out)
