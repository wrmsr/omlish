import json
import typing as ta

from omlish import marshal as msh

from .. import TextChatCompletionContentPart
from ..chatcompletion.message import AssistantChatCompletionMessage
from ..chatcompletion.request import ChatCompletionRequest
from ..chatcompletion.request import ChatCompletionRequestNamedToolChoice
from ..chatcompletion.responseformat import ChatCompletionResponseFormat
from ..chatcompletion.responseformat import TextChatCompletionResponseFormat


def test_marshal():
    for cls, obj in [
        (ChatCompletionResponseFormat, TextChatCompletionResponseFormat()),
        (AssistantChatCompletionMessage, AssistantChatCompletionMessage(content=(TextChatCompletionContentPart('hi'),))),  # noqa
        (ChatCompletionRequest, ChatCompletionRequest(messages=(), model='no', tool_choice='auto')),
        (ChatCompletionRequest, ChatCompletionRequest(messages=(), model='no', tool_choice=ChatCompletionRequestNamedToolChoice(ChatCompletionRequestNamedToolChoice.Function('barf')))),  # noqa
    ]:
        mv = msh.marshal(obj, cls)
        mj = json.dumps(mv)
        print(mj)

        obj2: ta.Any = msh.unmarshal(json.loads(mj), cls)
        assert obj2 == obj
