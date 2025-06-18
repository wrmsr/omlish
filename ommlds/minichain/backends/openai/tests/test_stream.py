from omlish.secrets.tests.harness import HarnessSecrets

from ....chat.choices.adapters import ChatChoicesServiceChatService
from ....chat.messages import UserMessage
from ....chat.services import ChatService
from ....chat.stream.adapters import ChatChoicesStreamServiceChatChoicesService
from ....chat.stream.services import ChatChoicesStreamRequest
from ....resources import Resources
from ....resources import UseResources
from ....services import Request
from ....standard import ApiKey
from ..stream import OpenaiChatChoicesStreamService


def test_openai_chat_stream_model(harness):
    llm = OpenaiChatChoicesStreamService(
        ApiKey(harness[HarnessSecrets].get_or_skip('openai_api_key').reveal()),
    )

    foo_req: ChatChoicesStreamRequest
    for foo_req in [
        ChatChoicesStreamRequest([UserMessage('Is water dry?')]),
        ChatChoicesStreamRequest([UserMessage('Is air wet?')]),
    ]:
        print(foo_req)

        with llm.invoke(foo_req).v as it:
            for o in it:
                print(o)
            print(it.outputs)


# def test_openai_stream_tools(harness):
#     tool_spec = ToolSpec(
#         'get_weather',
#         params=[
#             ToolParam(
#                 'location',
#                 type=ToolDtype.of(str),
#                 desc='The location to get the weather for.',
#             ),
#         ],
#         desc='Gets the weather in the given location.',
#     )
#
#     llm = OpenaiChatChoicesStreamService(
#         ApiKey(harness[HarnessSecrets].get_or_skip('openai_api_key').reveal()),
#     )
#
#     foo_req: ChatChoicesStreamRequest
#     foo_req = ChatChoicesStreamRequest(
#         [
#             SystemMessage("You are a helpful agent. Use any tools available to you to answer the user's questions."),
#             UserMessage('What is the weather in Seattle?'),
#             UserMessage(''),
#         ],
#         [
#             Tool(tool_spec),
#         ],
#     )
#
#     with llm.invoke(foo_req).v as it:
#         for o in it:
#             print(o)
#         print(it.outputs)


def test_use_resources(harness):
    llm = OpenaiChatChoicesStreamService(
        ApiKey(harness[HarnessSecrets].get_or_skip('openai_api_key').reveal()),
    )

    foo_req: ChatChoicesStreamRequest
    for foo_req in [
        ChatChoicesStreamRequest([UserMessage('Is water dry?')]),
        ChatChoicesStreamRequest([UserMessage('Is air wet?')]),
    ]:
        with Resources.new() as rs:
            print(foo_req)

            with llm.invoke(foo_req.with_options(UseResources(rs))).v as it:
                for o in it:
                    print(o)
                print(it.outputs)


def test_adapters(harness):
    llm: ChatService = ChatChoicesServiceChatService(
        ChatChoicesStreamServiceChatChoicesService(
            OpenaiChatChoicesStreamService(
                ApiKey(harness[HarnessSecrets].get_or_skip('openai_api_key').reveal()),
            ),
        ),
    )

    foo_req: Request
    for foo_req in [
        Request([UserMessage('Is water dry?')]),
        Request([UserMessage('Is air wet?')]),
    ]:
        print(llm.invoke(foo_req))
