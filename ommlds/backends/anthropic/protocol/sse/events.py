"""
https://docs.anthropic.com/en/docs/build-with-claude/streaming#content-block-delta-types
"""
import dataclasses as dc
import typing as ta

from omlish import lang

from ..types import Usage


##


class AnthropicSseDecoderEvents(lang.Namespace):
    class Event(lang.Abstract, lang.Sealed):
        pass

    #

    @dc.dataclass(frozen=True)
    class Ping(Event):
        pass

    #

    class MessageEvent(Event, lang.Abstract):
        pass

    @dc.dataclass(frozen=True)
    class MessageStart(MessageEvent):
        @dc.dataclass(frozen=True)
        class Message:
            id: str
            role: str
            model: str

            content: ta.Sequence[ta.Any]

            stop_reason: str | None = None
            stop_sequence: str | None = None

            usage: Usage | None = None

            type: ta.Literal['message'] | None = None

        message: Message

    @dc.dataclass(frozen=True)
    class MessageDelta(MessageEvent):
        @dc.dataclass(frozen=True)
        class Delta:
            stop_reason: str | None
            stop_sequence: ta.Any

        delta: Delta
        usage: Usage

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
            name: str
            input: ta.Any

        @dc.dataclass(frozen=True)
        class Thinking(ContentBlock):
            signature: str
            thinking: str

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

        @dc.dataclass(frozen=True)
        class ThinkingDelta(Delta):
            thinking: str

        @dc.dataclass(frozen=True)
        class SignatureDelta(Delta):
            signature: str

        delta: Delta
        index: int

    @dc.dataclass(frozen=True)
    class ContentBlockStop(ContentBlockEvent):
        index: int
