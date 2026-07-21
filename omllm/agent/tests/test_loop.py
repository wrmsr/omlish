import pytest

from omcore.secrets.tests.harness import HarnessSecrets

from ... import llm
from ..contexts import Context
from ..loop import Loop
from ..tools import Tool
from ..tools import ToolContext
from ..tools import ToolResult


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


##


async def execute_weather_tool(ctx: ToolContext) -> ToolResult:
    raise NotImplementedError


WEATHER_TOOL = Tool(
    llm_tool=llm.Tool(
        name='get_weather',
        description='Get the weather in a given location',
        params=[
            llm.ToolParam(
                name='location',
                description='The city and state, e.g. San Francisco, CA',
                type='string',
            ),
        ],
    ),
    executor=execute_weather_tool,
)


@pytest.mark.asyncs('asyncio')
@pytest.mark.online
async def test_loop_with_tool(harness):
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
                llm.UserMessage('What is the weather in Edinburgh, Scotland?'),
            ],
            tools=[
                WEATHER_TOOL,
            ],
        ),
    )

    loop_res = await loop.run()

    print(loop_res)
