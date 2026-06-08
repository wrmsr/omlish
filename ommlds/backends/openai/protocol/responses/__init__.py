# ruff: noqa: I001
"""
https://platform.openai.com/docs/api-reference/responses
"""
from .request import (  # noqa
    ResponsesInputContentPart,
    InputTextResponsesInputContentPart,
    OutputTextResponsesInputContentPart,
    InputImageResponsesInputContentPart,

    ResponsesInputItem,
    MessageResponsesInputItem,
    FunctionCallResponsesInputItem,
    FunctionCallOutputResponsesInputItem,
    ReasoningResponsesInputItem,

    ResponsesTool,
    FunctionResponsesTool,

    ResponsesRequest,
)

from .response import (  # noqa
    ResponsesOutputContentPart,
    OutputTextResponsesOutputContentPart,
    RefusalResponsesOutputContentPart,

    ResponsesOutputItem,
    MessageResponsesOutputItem,
    FunctionCallResponsesOutputItem,
    ReasoningResponsesOutputItem,

    ResponsesUsage,
    ResponsesResponse,
)

from .events import (  # noqa
    ResponsesSseEvents,
)


##


from omlish import marshal as _msh  # noqa

_msh.register_global_module_import('._marshal', __package__)
