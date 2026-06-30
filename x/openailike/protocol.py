import dataclasses as dc
import typing as ta


##


class OaiLikeChatCompletionContentPart:
    pass


@dc.dataclass(frozen=True, kw_only=True)
class TextOaiLikeChatCompletionContentPart(OaiLikeChatCompletionContentPart):
    text: str
    type: ta.Literal['text'] = 'text'


##


class OaiLikeChatCompletionMessage:
    pass


@dc.dataclass(frozen=True, kw_only=True)
class SystemOaiLikeChatCompletionMessage[
    TextPartT: TextOaiLikeChatCompletionContentPart = TextOaiLikeChatCompletionContentPart,
](
    OaiLikeChatCompletionMessage,
):
    content: str | ta.Iterable[TextPartT]
    role: ta.Literal['system'] = 'system'


@dc.dataclass(frozen=True, kw_only=True)
class UserOaiLikeChatCompletionMessage[
    TextPartT: TextOaiLikeChatCompletionContentPart = TextOaiLikeChatCompletionContentPart,
](
    OaiLikeChatCompletionMessage,
):
    content: str | ta.Iterable[TextPartT]
    role: ta.Literal['user'] = 'user'


@dc.dataclass(frozen=True, kw_only=True)
class AssistantOaiLikeChatCompletionMessage[
    PartT: OaiLikeChatCompletionContentPart = OaiLikeChatCompletionContentPart,
](
    OaiLikeChatCompletionMessage,
):
    content: str | ta.Iterable[PartT]
    role: ta.Literal['assistant'] = 'assistant'


##


@dc.dataclass(frozen=True, kw_only=True)
class OaiLikeChatCompletionChoice[
    MessageT,
]:
    index: int
    message: MessageT
    finish_reason: str | None


@dc.dataclass(frozen=True, kw_only=True)
class OaiLikeChatCompletionUsage:
    completion_tokens: int
    prompt_tokens: int
    total_tokens: int


@dc.dataclass(frozen=True, kw_only=True)
class OaiLikeChatCompletionResponse[
    ChoiceT: OaiLikeChatCompletionChoice = OaiLikeChatCompletionChoice,
    UsageT: OaiLikeChatCompletionUsage = OaiLikeChatCompletionUsage,
]:
    id: str
    object: ta.Literal['chat.completion'] = 'chat.completion'
    created: int
    model: str
    choices: ta.Sequence[ChoiceT]
    usage: UsageT | None = None


###


class GroqChatCompletionContentPart(OaiLikeChatCompletionContentPart):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class TextGroqChatCompletionContentPart(
    TextOaiLikeChatCompletionContentPart,
    GroqChatCompletionContentPart,
):
    text: str
    type: ta.Literal['text'] = 'text'


##


class GroqChatCompletionMessage(OaiLikeChatCompletionMessage):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class SystemGroqChatCompletionMessage(
    SystemOaiLikeChatCompletionMessage[
        TextGroqChatCompletionContentPart,
    ],
    GroqChatCompletionMessage,
):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class UserGroqChatCompletionMessage(
    UserOaiLikeChatCompletionMessage[
        TextGroqChatCompletionContentPart,
    ],
    GroqChatCompletionMessage,
):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class AssistantGroqChatCompletionMessage(
    AssistantOaiLikeChatCompletionMessage[
        GroqChatCompletionContentPart,
    ],
    GroqChatCompletionMessage,
):
    pass


##


@dc.dataclass(frozen=True, kw_only=True)
class GroqChatCompletionChoice(
    OaiLikeChatCompletionChoice[
        GroqChatCompletionMessage,
    ],
):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class GroqChatCompletionResponse(
    OaiLikeChatCompletionResponse[
        GroqChatCompletionChoice,
    ],
):
    pass


##


def _main() -> None:
    from omlish import reflect2 as rfl

    for cls in [
        OaiLikeChatCompletionResponse,
        GroqChatCompletionResponse,
    ]:
        rty = rfl.reflect_type(cls)
        print(rty)


if __name__ == '__main__':
    _main()
