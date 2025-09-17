"""
https://platform.openai.com/docs/api-reference/introduction
https://github.com/openai/openai-openapi/blob/master/openapi.yaml
"""
# ruff: noqa: I001

from .chatcompletion.chunk import (  # noqa
    ChatCompletionChunkChoiceDelta,

    ChatCompletionChunkChoice,

    ChatCompletionChunk,
)

from .chatcompletion.contentpart import (  # noqa
    TextChatCompletionContentPart,

    ImageUrlChatCompletionContentPart,

    FileChatCompletionContentPart,

    InputAudioChatCompletionContentPart,

    RefusalChatCompletionContentPart,

    ChatCompletionContentPart,
)

from .chatcompletion.message import (  # noqa
    DeveloperChatCompletionMessage,

    SystemChatCompletionMessage,

    UserChatCompletionMessage,

    AssistantChatCompletionMessage,

    ToolChatCompletionMessage,

    FunctionChatCompletionMessage,

    ChatCompletionMessage,
)

from .chatcompletion.request import (  # noqa
    ChatCompletionRequestWebSearchOptions,

    ChatCompletionRequestPrediction,

    ChatCompletionRequestTool,

    ChatCompletionRequestNamedToolChoice,

    ChatCompletionRequestAudio,

    ChatCompletionRequest,
)

from .chatcompletion.response import (  # noqa
    ChatCompletionResponseMessage,

    ChatCompletionResponseChoice,

    ChatCompletionResponse,
)

from .chatcompletion.responseformat import (  # noqa
    TextChatCompletionResponseFormat,

    JsonSchemaChatCompletionResponseFormat,

    JsonObjectChatCompletionResponseFormat,

    ChatCompletionResponseFormat,
)

from .chatcompletion.tokenlogprob import (  # noqa
    ChatCompletionTokenLogprob,
)

from .completionusage import (  # noqa
    CompletionUsage,
)


##


from omlish import marshal as _msh  # noqa

_msh.register_global_module_import('._marshal', __package__)
