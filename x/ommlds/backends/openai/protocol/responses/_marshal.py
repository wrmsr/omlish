from omcore import marshal as msh

from .events import ResponsesSseEvents
from .request import ResponsesInputContentPart
from .request import ResponsesInputItem
from .request import ResponsesTool
from .response import ResponsesOutputContentPart
from .response import ResponsesOutputItem


##


@msh.register_global_lazy_init
def _install_standard_marshaling(cfgs: msh.ConfigRegistry) -> None:
    for root_cls, tag_field in [
        (ResponsesInputContentPart, 'type'),
        (ResponsesInputItem, 'type'),
        (ResponsesTool, 'type'),
        (ResponsesOutputContentPart, 'type'),
        (ResponsesOutputItem, 'type'),
    ]:
        msh.install_standard_factories(
            cfgs,
            *msh.standard_polymorphism_factories(
                msh.polymorphism_from_subclasses(
                    root_cls,
                    naming=msh.Naming.SNAKE,
                    strip_suffix=msh.AUTO_STRIP_SUFFIX,
                ),
                msh.FieldTypeTagging(tag_field),
            ),
        )

    # Sse event type tags are dotted - explicit impls.
    msh.install_standard_factories(
        cfgs,
        *msh.standard_polymorphism_factories(
            msh.Polymorphism(
                ResponsesSseEvents.Event,
                [
                    msh.Impl(ResponsesSseEvents.Created, 'response.created'),
                    msh.Impl(ResponsesSseEvents.InProgress, 'response.in_progress'),
                    msh.Impl(ResponsesSseEvents.Completed, 'response.completed'),
                    msh.Impl(ResponsesSseEvents.Failed, 'response.failed'),
                    msh.Impl(ResponsesSseEvents.Incomplete, 'response.incomplete'),

                    msh.Impl(ResponsesSseEvents.OutputItemAdded, 'response.output_item.added'),
                    msh.Impl(ResponsesSseEvents.OutputItemDone, 'response.output_item.done'),

                    msh.Impl(ResponsesSseEvents.ContentPartAdded, 'response.content_part.added'),
                    msh.Impl(ResponsesSseEvents.ContentPartDone, 'response.content_part.done'),

                    msh.Impl(ResponsesSseEvents.OutputTextDelta, 'response.output_text.delta'),
                    msh.Impl(ResponsesSseEvents.OutputTextDone, 'response.output_text.done'),

                    msh.Impl(ResponsesSseEvents.FunctionCallArgumentsDelta, 'response.function_call_arguments.delta'),
                    msh.Impl(ResponsesSseEvents.FunctionCallArgumentsDone, 'response.function_call_arguments.done'),

                    msh.Impl(ResponsesSseEvents.ReasoningSummaryPartAdded, 'response.reasoning_summary_part.added'),
                    msh.Impl(ResponsesSseEvents.ReasoningSummaryPartDone, 'response.reasoning_summary_part.done'),
                    msh.Impl(ResponsesSseEvents.ReasoningSummaryTextDelta, 'response.reasoning_summary_text.delta'),
                    msh.Impl(ResponsesSseEvents.ReasoningSummaryTextDone, 'response.reasoning_summary_text.done'),
                    msh.Impl(ResponsesSseEvents.ReasoningTextDelta, 'response.reasoning_text.delta'),
                    msh.Impl(ResponsesSseEvents.ReasoningTextDone, 'response.reasoning_text.done'),

                    msh.Impl(ResponsesSseEvents.Error, 'error'),
                ],
            ),
            msh.FieldTypeTagging('type'),
        ),
    )
