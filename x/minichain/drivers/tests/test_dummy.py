import typing as ta
import uuid

import pytest  # noqa

from omcore import check
from omcore import inject as inj

from ...chat.choices.services import ChatChoicesRequest
from ...chat.choices.services import ChatChoicesResponse
from ...chat.choices.services import ChatChoicesService
from ...chat.choices.services import static_check_is_chat_choices_service
from ...chat.choices.types import ChatChoices
from ...chat.generations import ChatGeneration
from ...chat.messages import AiMessage
from ...chat.messages import Chat
from ...chat.messages import ToolUseMessage
from ...chat.messages import ToolUseResultMessage
from ...chat.messages import UserMessage
from ...tools.execution.catalog import ToolCatalog
from ...tools.execution.catalog import ToolCatalogEntries
from ...tools.execution.catalog import ToolCatalogEntry
from ...tools.execution.execution import ToolUseExecution
from ...tools.execution.execution import ToolUseExecutor
from ...tools.execution.invokers import ToolInvoker
from ...tools.types import ToolSpec
from ...tools.types import ToolUse
from ...tools.types import ToolUseResult
from ..ai.tools import ToolExecutingAiChatGenerator
from ..ai.types import AiChatGenerator
from ..ai.types import GenerateAiChatArgs
from ..configs import DriverConfig
from ..inject import bind_driver
from ..storage.types import ChatId
from ..types import Driver
from ..user.configs import UserConfig


@static_check_is_chat_choices_service
class DummyChatChoicesService:
    async def invoke(self, request: ChatChoicesRequest) -> ChatChoicesResponse:
        return ChatChoicesResponse(ChatChoices([ChatGeneration([AiMessage(f'*Ai Message {len(request.v) + 1}*')])]))


class _NoopToolInvoker(ToolInvoker):
    async def invoke_tool(
            self,
            name: str,
            args: ta.Mapping[str, ta.Any],
    ) -> str:
        raise NotImplementedError


class _RecordingAiChatGenerator(AiChatGenerator):
    def __init__(self, responses: ta.Sequence[Chat]) -> None:
        super().__init__()

        self._responses = list(responses)
        self.chats: list[Chat] = []

    async def generate_ai_chat(self, args: GenerateAiChatArgs) -> Chat:
        self.chats.append(args.chat)
        return self._responses.pop(0)


class _RecordingToolUseExecutor(ToolUseExecutor):
    def __init__(self) -> None:
        super().__init__()

        self.executions: list[ToolUseExecution] = []

    async def execute_tool_use(self, tue: ToolUseExecution) -> ToolUseResult:
        self.executions.append(tue)
        return ToolUseResult(
            id=tue.use.id,
            name=tue.use.name,
            c=f'{tue.use.name} result',
        )


@pytest.mark.asyncs('asyncio')
async def test_tool_executing_ai_chat_generator_batches_parallel_tool_results():
    use_a = ToolUseMessage(ToolUse(
        id='call_a',
        name='tool_a',
        args={},
        raw_args='{}',
    ))
    use_b = ToolUseMessage(ToolUse(
        id='call_b',
        name='tool_b',
        args={},
        raw_args='{}',
    ))

    wrapped = _RecordingAiChatGenerator([
        [use_a, use_b],
        [AiMessage('done')],
    ])
    executor = _RecordingToolUseExecutor()

    gen = ToolExecutingAiChatGenerator(
        wrapped=wrapped,
        catalog=ToolCatalog(ToolCatalogEntries([
            ToolCatalogEntry(ToolSpec('tool_a'), _NoopToolInvoker()),
            ToolCatalogEntry(ToolSpec('tool_b'), _NoopToolInvoker()),
        ])),
        executor=executor,
    )

    out = await gen.generate_ai_chat(GenerateAiChatArgs([UserMessage('go')]))

    assert [type(m) for m in out] == [
        ToolUseMessage,
        ToolUseMessage,
        ToolUseResultMessage,
        ToolUseResultMessage,
        AiMessage,
    ]
    assert [e.use.id for e in executor.executions] == ['call_a', 'call_b']

    second_chat = wrapped.chats[1]
    assert [type(m) for m in second_chat[-4:]] == [
        ToolUseMessage,
        ToolUseMessage,
        ToolUseResultMessage,
        ToolUseResultMessage,
    ]
    tool_result_messages = [
        check.isinstance(m, ToolUseResultMessage)
        for m in second_chat[-2:]
    ]
    assert [m.tur.id for m in tool_result_messages] == ['call_a', 'call_b']


def bind_test_driver(
        cfg: DriverConfig = DriverConfig(),
) -> inj.Elements:
    els: list[inj.Elemental] = []

    els.extend([
        bind_driver(cfg),

        inj.bind(ChatChoicesService, to_ctor=DummyChatChoicesService),

        inj.bind(ChatId(uuid.uuid7())),
    ])

    return inj.as_elements(*els)


@pytest.mark.asyncs('asyncio')
async def test_inject():
    async with inj.create_async_managed_injector(bind_test_driver(
        cfg=DriverConfig(
            user=UserConfig(
                initial_user_content='Hi!',
            ),
        ),
    )) as injector:
        driver = await injector[Driver]
        assert driver


@pytest.mark.asyncs('asyncio')
async def test_driver():
    async with inj.create_async_managed_injector(bind_test_driver(
        cfg=DriverConfig(
            user=UserConfig(
                initial_user_content='Hi!',
            ),
        ),
    )) as injector:
        driver = await injector[Driver]

        await driver.start()
        await driver.stop()
