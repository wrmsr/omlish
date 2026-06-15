# """
# Offline coverage of StopReason wiring through the driver: every generated segment's terminal message carries a
# `StopReasonMessageMetadata` - structurally inferred (tool-use terminus -> ToolUse, else EndTurn) and overridable by a
# backend's explicit `StopReasonOutput` (here driven through the scripted backend's per-turn outputs).
# """
# import pytest
#
# from omlish import check
# from omlish import inject as inj
#
# from ...backends.scripted.scripts import ChatScript
# from ...backends.scripted.scripts import ChatScriptTurn
# from ...chat.messages import AiMessage
# from ...chat.messages import ToolUseMessage
# from ...chat.messages import UserMessage
# from ...chat.metadata import StopReasonMessageMetadata
# from ...llms.types import EndTurnStopReason
# from ...llms.types import MaxTokensStopReason
# from ...llms.types import StopReasonOutput
# from ...llms.types import ToolUseStopReason
# from ...modules.weathertest.inject import bind_weather_test
# from ...tools.types import ToolUse
# from ..actions import SendUserMessagesAction
# from ..ai.configs import AiConfig
# from ..configs import DriverConfig
# from ..storage.manager import DriverStorageManager
# from ..testing import bind_scripted_driver
# from ..types import Driver
#
#
# def _stop_reason(msg):
#     return check.not_none(msg.metadata.get(StopReasonMessageMetadata)).v
#
#
# @pytest.mark.parametrize('stream', [False, True])
# @pytest.mark.asyncs('asyncio')
# async def test_stop_reason_tool_loop_and_explicit_override(stream):
#     # Segment 1 ends in a tool call (-> ToolUse, structurally). Segment 2 ends in prose carrying an explicit
#     # MaxTokens output - the terminus is not a tool use, so the explicit reason wins.
#     script = ChatScript([
#         ChatScriptTurn.of(
#             AiMessage('Checking the weather.'),
#             ToolUseMessage(ToolUse(id='call_1', name='weather', args={'location': 'Tokyo'})),
#         ),
#         ChatScriptTurn.of(
#             AiMessage('It is foggy in Tokyo.'),
#             outputs=[StopReasonOutput(MaxTokensStopReason())],
#         ),
#     ])
#
#     async with inj.create_async_managed_injector(
#         bind_scripted_driver(
#             script,
#             DriverConfig(ai=AiConfig(stream=stream, enable_tools=True)),
#         ),
#         bind_weather_test(),
#     ) as injector:
#         driver = await injector[Driver]
#
#         await driver.start()
#         await driver.do_action(SendUserMessagesAction([UserMessage('what is the weather in tokyo?')]))
#         await driver.stop()
#
#         chat = await (await injector[DriverStorageManager]).get_chat()
#
#     # [UserMessage, AiMessage, ToolUseMessage, ToolUseResultMessage, AiMessage]
#     tu_msg = check.isinstance(chat[2], ToolUseMessage)
#     assert isinstance(_stop_reason(tu_msg), ToolUseStopReason)
#
#     final = check.isinstance(chat[4], AiMessage)
#     assert isinstance(_stop_reason(final), MaxTokensStopReason)
#
#
# @pytest.mark.parametrize('stream', [False, True])
# @pytest.mark.asyncs('asyncio')
# async def test_stop_reason_plain_turn_infers_end_turn(stream):
#     script = ChatScript([
#         ChatScriptTurn.of(
#             AiMessage('a plain considered response'),
#         ),
#     ])
#
#     async with inj.create_async_managed_injector(
#         bind_scripted_driver(script, DriverConfig(ai=AiConfig(stream=stream))),
#     ) as injector:
#         driver = await injector[Driver]
#
#         await driver.start()
#         await driver.do_action(SendUserMessagesAction([UserMessage('hi')]))
#         await driver.stop()
#
#         chat = await (await injector[DriverStorageManager]).get_chat()
#
#     final = check.isinstance(chat[-1], AiMessage)
#     assert isinstance(_stop_reason(final), EndTurnStopReason)
