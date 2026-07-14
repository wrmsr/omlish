"""https://platform.openai.com/docs/api-reference/responses-streaming"""
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .._common import _set_class_marshal_options
from .response import ResponsesOutputContentPart
from .response import ResponsesOutputItem
from .response import ResponsesResponse


##


class ResponsesSseEvents(lang.Namespace):
    class Event(lang.Abstract, lang.Sealed):
        pass

    ##
    # Response lifecycle - tags: response.created / response.in_progress / response.completed / response.failed /
    # response.incomplete

    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options
    class ResponseEvent(Event, lang.Abstract):
        response: ResponsesResponse

        sequence_number: int | None = None

    class Created(ResponseEvent, lang.Final):
        pass

    class InProgress(ResponseEvent, lang.Final):
        pass

    class Completed(ResponseEvent, lang.Final):
        pass

    class Failed(ResponseEvent, lang.Final):
        pass

    class Incomplete(ResponseEvent, lang.Final):
        pass

    ##
    # Output items - tags: response.output_item.added / response.output_item.done

    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options
    class OutputItemEvent(Event, lang.Abstract):
        output_index: int
        item: ResponsesOutputItem

        sequence_number: int | None = None

    class OutputItemAdded(OutputItemEvent, lang.Final):
        pass

    class OutputItemDone(OutputItemEvent, lang.Final):
        pass

    ##
    # Content parts - tags: response.content_part.added / response.content_part.done

    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options
    class ContentPartEvent(Event, lang.Abstract):
        item_id: str
        output_index: int
        content_index: int
        part: ResponsesOutputContentPart

        sequence_number: int | None = None

    class ContentPartAdded(ContentPartEvent, lang.Final):
        pass

    class ContentPartDone(ContentPartEvent, lang.Final):
        pass

    ##
    # Output text - tags: response.output_text.delta / response.output_text.done

    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options
    class OutputTextDelta(Event, lang.Final):
        item_id: str
        output_index: int
        content_index: int
        delta: str

        logprobs: ta.Sequence[ta.Any] | None = None
        obfuscation: str | None = None
        sequence_number: int | None = None

    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options
    class OutputTextDone(Event, lang.Final):
        item_id: str
        output_index: int
        content_index: int
        text: str

        logprobs: ta.Sequence[ta.Any] | None = None
        sequence_number: int | None = None

    ##
    # Function call arguments - tags: response.function_call_arguments.delta / response.function_call_arguments.done

    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options
    class FunctionCallArgumentsDelta(Event, lang.Final):
        item_id: str
        output_index: int
        delta: str

        obfuscation: str | None = None
        sequence_number: int | None = None

    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options
    class FunctionCallArgumentsDone(Event, lang.Final):
        item_id: str
        output_index: int
        arguments: str

        name: str | None = None
        sequence_number: int | None = None

    ##
    # Reasoning summaries / text - tags: response.reasoning_summary_part.added / ...done /
    # response.reasoning_summary_text.delta / ...done / response.reasoning_text.delta / ...done

    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options
    class ReasoningSummaryPartEvent(Event, lang.Abstract):
        item_id: str
        output_index: int
        summary_index: int
        part: ta.Any

        sequence_number: int | None = None

    class ReasoningSummaryPartAdded(ReasoningSummaryPartEvent, lang.Final):
        pass

    class ReasoningSummaryPartDone(ReasoningSummaryPartEvent, lang.Final):
        pass

    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options
    class ReasoningSummaryTextDelta(Event, lang.Final):
        item_id: str
        output_index: int
        summary_index: int
        delta: str

        obfuscation: str | None = None
        sequence_number: int | None = None

    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options
    class ReasoningSummaryTextDone(Event, lang.Final):
        item_id: str
        output_index: int
        summary_index: int
        text: str

        sequence_number: int | None = None

    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options
    class ReasoningTextDelta(Event, lang.Final):
        item_id: str
        output_index: int
        content_index: int
        delta: str

        obfuscation: str | None = None
        sequence_number: int | None = None

    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options
    class ReasoningTextDone(Event, lang.Final):
        item_id: str
        output_index: int
        content_index: int
        text: str

        sequence_number: int | None = None

    ##
    # Errors - tag: error

    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options
    class Error(Event, lang.Final):
        message: str

        code: str | None = None
        param: str | None = None
        sequence_number: int | None = None
