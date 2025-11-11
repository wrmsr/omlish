from omlish import check

from .....backends.groq import protocol as pt
from ....chat.choices.services import ChatChoicesResponse
from ....chat.choices.types import AiChoice
from ....chat.messages import AiMessage
from ....chat.messages import Message
from ....chat.messages import SystemMessage
from ....chat.messages import UserMessage
from ....chat.stream.types import AiChoiceDeltas
from ....chat.stream.types import ContentAiChoiceDelta


##


def build_gq_request_message(mc_msg: Message) -> pt.ChatCompletionRequest.Message:
    if isinstance(mc_msg, SystemMessage):
        return pt.ChatCompletionRequest.SystemMessage(
            content=check.isinstance(mc_msg.c, str),
        )

    elif isinstance(mc_msg, UserMessage):
        return pt.ChatCompletionRequest.UserMessage(
            content=check.isinstance(mc_msg.c, str),
        )

    else:
        raise TypeError(mc_msg)


def build_mc_choices_response(gq_resp: pt.ChatCompletionResponse) -> ChatChoicesResponse:
    return ChatChoicesResponse([
        AiChoice([AiMessage(
            check.isinstance(gq_choice.message.content, str),
        )])
        for gq_choice in gq_resp.choices
    ])


def build_mc_ai_choice_deltas(delta: pt.ChatCompletionChunk.Choice.Delta) -> AiChoiceDeltas:
    if delta.role in (None, 'assistant') and delta.content is not None:
        return AiChoiceDeltas([ContentAiChoiceDelta(delta.content)])

    else:
        return AiChoiceDeltas([])
