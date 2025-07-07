import dataclasses as dc
import typing as ta

from omlish import lang


##


class AnthropicSseDecoderEvents(lang.Namespace):
    class Event(lang.Abstract, lang.Sealed):
        pass

    #

    @dc.dataclass(frozen=True)
    class Ping(Event):
        pass

    #

    @dc.dataclass(frozen=True, kw_only=True)
    class Usage:
        input_tokens: int | None = None
        cache_creation_input_tokens: int | None = None
        cache_read_input_tokens: int | None = None
        output_tokens: int | None = None
        service_tier: str | None = None

    #

    class MessageEvent(Event, lang.Abstract):
        pass

    @dc.dataclass(frozen=True)
    class MessageStart(MessageEvent):
        @dc.dataclass(frozen=True)
        class Message:
            type: ta.Literal['message'] | None
            id: str
            role: str
            model: str
            content: ta.Sequence[ta.Any]
            stop_reason: str | None
            stop_sequence: str | None
            usage: 'AnthropicSseDecoderEvents.Usage'

        message: Message

    @dc.dataclass(frozen=True)
    class MessageDelta(MessageEvent):
        @dc.dataclass(frozen=True)
        class Delta:
            stop_reason: str | None
            stop_sequence: ta.Any

        delta: Delta
        usage: 'AnthropicSseDecoderEvents.Usage'

    @dc.dataclass(frozen=True)
    class MessageStop(MessageEvent):
        pass

    #

    class ContentBlockEvent(Event, lang.Abstract):
        pass

    @dc.dataclass(frozen=True)
    class ContentBlockStart(ContentBlockEvent):
        class ContentBlock(lang.Abstract):
            pass

        @dc.dataclass(frozen=True)
        class Text(ContentBlock):
            text: str

        @dc.dataclass(frozen=True)
        class ToolUse(ContentBlock):
            id: str
            input: ta.Any
            name: str

        content_block: ContentBlock
        index: int

    @dc.dataclass(frozen=True)
    class ContentBlockDelta(ContentBlockEvent):
        class Delta(lang.Abstract):
            pass

        @dc.dataclass(frozen=True)
        class TextDelta(Delta):
            text: str

        @dc.dataclass(frozen=True)
        class InputJsonDelta(Delta):
            partial_json: str

        delta: Delta
        index: int

    @dc.dataclass(frozen=True)
    class ContentBlockStop(ContentBlockEvent):
        index: int
