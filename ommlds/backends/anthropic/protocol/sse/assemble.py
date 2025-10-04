import typing as ta

from omlish import check
from omlish.formats import json
from omlish.funcs import genmachine

from ..types import Content
from ..types import Message
from ..types import Text
from ..types import ToolUse
from ..types import Usage
from .events import AnthropicSseDecoderEvents


##


class AnthropicSseMessageAssembler(
    genmachine.GenMachine[
        AnthropicSseDecoderEvents.Event,
        Message,
    ],
):
    def __init__(self) -> None:
        super().__init__(self._do_main())

    #

    _UNINTERESTING_EVENT_TYPES: tuple[type[AnthropicSseDecoderEvents.Event], ...] = (
        AnthropicSseDecoderEvents.Ping,
    )

    def _next_event(self):
        while True:
            ae = yield None  # noqa
            if ae is None:
                return ae
            elif isinstance(ae, self._UNINTERESTING_EVENT_TYPES):
                continue
            elif isinstance(ae, AnthropicSseDecoderEvents.Event):
                return ae
            else:
                raise TypeError(ae)

    def _do_main(self):
        while True:
            ae = yield from self._next_event()
            if ae is None:
                return None
            elif isinstance(ae, AnthropicSseDecoderEvents.MessageStart):
                return self._do_message(ae)
            else:
                raise TypeError(ae)

    def _do_message(self, ms: AnthropicSseDecoderEvents.MessageStart) -> ta.Any:
        check.empty(ms.message.content)
        content: list[Content] = []
        dct: dict[str, ta.Any] = dict(
            stop_reason=ms.message.stop_reason,
            stop_sequence=ms.message.stop_sequence,
        )
        usage: Usage | None = ms.message.usage
        while True:
            ae: ta.Any = check.not_none((yield from self._next_event()))
            if isinstance(ae, AnthropicSseDecoderEvents.ContentBlockStart):
                # check.equal(ae.index, len(content))
                c = yield from self._do_content_block(ae)
                if c is not None:
                    content.append(check.isinstance(c, Content))
            elif isinstance(ae, AnthropicSseDecoderEvents.MessageDelta):
                for k in ('stop_reason', 'stop_sequence'):
                    if (v := getattr(ae.delta, k)) is not None:
                        check.none(dct[k])
                        dct[k] = v
                if ae.usage is not None:
                    usage = ae.usage
            elif isinstance(ae, AnthropicSseDecoderEvents.MessageStop):
                yield [Message(
                    id=ms.message.id,
                    role=ms.message.role,  # type: ignore[arg-type]
                    model=ms.message.model,
                    content=content,
                    stop_reason=dct['stop_reason'],
                    stop_sequence=dct['stop_sequence'],
                    usage=usage,
                )]
                return self._do_main()
            else:
                raise TypeError(ae)

    def _do_content_block(self, cbs: AnthropicSseDecoderEvents.ContentBlockStart) -> ta.Any:
        if isinstance(cbs.content_block, AnthropicSseDecoderEvents.ContentBlockStart.Text):
            return (yield from self._do_text_content_block(cbs))
        elif isinstance(cbs.content_block, AnthropicSseDecoderEvents.ContentBlockStart.ToolUse):
            return (yield from self._do_tool_use_content_block(cbs))
        elif isinstance(cbs.content_block, AnthropicSseDecoderEvents.ContentBlockStart.Thinking):
            return (yield from self._do_thinking_content_block(cbs))
        else:
            raise TypeError(cbs.content_block)

    def _do_text_content_block(self, cbs: AnthropicSseDecoderEvents.ContentBlockStart) -> ta.Any:
        csc = check.isinstance(cbs.content_block, AnthropicSseDecoderEvents.ContentBlockStart.Text)
        parts: list[str] = [csc.text]
        while True:
            ae: ta.Any = check.not_none((yield from self._next_event()))
            if isinstance(ae, AnthropicSseDecoderEvents.ContentBlockDelta):
                # check.equal(ae.index, cbs.index)
                cdc = check.isinstance(ae.delta, AnthropicSseDecoderEvents.ContentBlockDelta.TextDelta)
                parts.append(cdc.text)
            elif isinstance(ae, AnthropicSseDecoderEvents.ContentBlockStop):
                # check.equal(ae.index, cbs.index)
                return Text(''.join(parts))
            else:
                raise TypeError(ae)

    def _do_tool_use_content_block(self, cbs: AnthropicSseDecoderEvents.ContentBlockStart) -> ta.Any:
        csc = check.isinstance(cbs.content_block, AnthropicSseDecoderEvents.ContentBlockStart.ToolUse)
        dct: dict[str, ta.Any] = {}
        if csc.input is not None:
            dct.update({check.non_empty_str(k): v for k, v in check.isinstance(csc.input, ta.Mapping).items()})
        json_parts: list[str] = []
        while True:
            ae: ta.Any = check.not_none((yield from self._next_event()))
            if isinstance(ae, AnthropicSseDecoderEvents.ContentBlockDelta):
                # check.equal(ae.index, cbs.index)
                cdc = check.isinstance(ae.delta, AnthropicSseDecoderEvents.ContentBlockDelta.InputJsonDelta)
                json_parts.append(cdc.partial_json)
            elif isinstance(ae, AnthropicSseDecoderEvents.ContentBlockStop):
                # check.equal(ae.index, cbs.index)
                dj = ''.join(json_parts).strip()
                if dj:
                    dd = check.isinstance(json.loads(dj), ta.Mapping)
                    for k, v in dd.items():
                        k = check.non_empty_str(k)
                        check.not_in(k, dct)
                        dct[k] = v
                return ToolUse(
                    id=check.non_empty_str(csc.id),
                    input=dct,
                    name=check.non_empty_str(csc.name),
                )
            else:
                raise TypeError(ae)

    def _do_thinking_content_block(self, cbs: AnthropicSseDecoderEvents.ContentBlockStart) -> ta.Any:
        # csc = check.isinstance(cbs.content_block, AnthropicSseDecoderEvents.ContentBlockStart.Thinking)
        while True:
            ae: ta.Any = check.not_none((yield from self._next_event()))
            if isinstance(ae, AnthropicSseDecoderEvents.ContentBlockDelta):
                pass
            elif isinstance(ae, AnthropicSseDecoderEvents.ContentBlockStop):
                return None
            else:
                raise TypeError(ae)
        return  # type: ignore  # noqa
        yield  # noqa
