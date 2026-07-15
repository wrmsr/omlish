import pytest

from omcore.secrets.tests.harness import HarnessSecrets

from .....models.default import default_model_catalog
from .....types.context import Context
from .....types.messages import UserMessage
from .....types.models import ModelKey
from .....types.options import Options
from .....types.tools import Tool
from .....types.tools import ToolParam
from ..immediate import OpenaiCompletionsImmediateBackend


class BaseBackendTest:
    @pytest.mark.online
    @pytest.mark.asyncs('asyncio')
    @pytest.mark.parametrize('max_tokens', [None, 1024])
    async def test_backend(
            self,
            harness,
            model,
            max_tokens,
    ):
        model_key, api_key_name = model

        svc = OpenaiCompletionsImmediateBackend(
            default_model_catalog()[model_key],  # noqa
            api_key=harness[HarnessSecrets].get_or_skip(api_key_name),
        )

        out = await svc.immediate(
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


class TestOpenaiBackend(BaseBackendTest):
    @pytest.fixture(params=[
        (ModelKey('openai', 'gpt-5.4-mini'), 'openai_api_key'),
    ])
    def model(self, request):
        return request.param


class TestGroqBackend(BaseBackendTest):
    @pytest.fixture(params=[
        (ModelKey('groq', 'openai/gpt-oss-120b'), 'groq_api_key'),
    ])
    def model(self, request):
        return request.param


class TestCerebrasBackend(BaseBackendTest):
    @pytest.fixture(params=[
        (ModelKey('cerebras', 'gpt-oss-120b'), 'cerebras_api_key'),
    ])
    def model(self, request):
        return request.param


@pytest.mark.online
@pytest.mark.asyncs('asyncio')
async def test_openai_tools(harness):
    model_key, api_key_name = (ModelKey('openai', 'gpt-5.4-mini'), 'openai_api_key')

    svc = OpenaiCompletionsImmediateBackend(
        default_model_catalog()[model_key],  # noqa
        api_key=harness[HarnessSecrets].get_or_skip(api_key_name),
    )

    out = await svc.immediate(
        Context(
            system_prompt='You are a helpful assistant.',
            messages=[
                UserMessage('hi'),
            ],
            tools=[
                Tool(
                    name='get_weather',
                    description='Get the weather in a given location',
                    params=[
                        ToolParam(
                            name='location',
                            description='The city and state, e.g. San Francisco, CA',
                            type='string',
                        ),
                    ],
                ),
            ],
        ),
    )

    print(out)
