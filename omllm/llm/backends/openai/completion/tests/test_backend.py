import pytest

from omlish.secrets.tests.harness import HarnessSecrets

from .....types.context import Context
from .....types.messages import UserMessage
from ..backend import CompletionOpenaiBackend


@pytest.mark.asyncs('asyncio')
async def test_backend(harness):
    svc = CompletionOpenaiBackend(
        api_key=harness[HarnessSecrets].get_or_skip('openai_api_key'),
    )

    out = await svc.complete(Context(
        system_prompt='You are a helpful assistant.',
        messages=[
            UserMessage('hi'),
        ],
    ))

    print(out)
