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
class UserOiaLikeChatCompletionMessage[
    TextPartT: TextOaiLikeChatCompletionContentPart = TextOaiLikeChatCompletionContentPart,
](
    OaiLikeChatCompletionMessage,
):
    content: str | ta.Iterable[TextPartT]
    role: ta.Literal['user'] = 'user'


@dc.dataclass(frozen=True, kw_only=True)
class AssistantOiaLikeChatCompletionMessage[
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


##


def _main() -> None:
    from omlish import reflect2 as rfl

    rty = rfl.reflect_type(OaiLikeChatCompletionResponse)

    print(rty)


if __name__ == '__main__':
    _main()
