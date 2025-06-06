"""
https://platform.openai.com/docs/api-reference/introduction
https://github.com/openai/openai-openapi/blob/master/openapi.yaml
"""
# ruff: noqa: I001

from .chatcompletion.chunk import (  # noqa
    ChatCompletionChunkChoiceDeltaToolCallFunction,
    ChatCompletionChunkChoiceDeltaToolCall,
    ChatCompletionChunkChoiceDelta,

    ChatCompletionChunkChoiceLogprobs,
    ChatCompletionChunkChoice,

    ChatCompletionChunk,
)

from .chatcompletion.contentpart import (  # noqa
    TextChatCompletionContentPart,

    ImageChatCompletionContentPartImageUrl,
    ImageChatCompletionContentPart,

    FileChatCompletionContentPartFileInfo,
    FileChatCompletionContentPart,

    InputAudioChatCompletionContentPartInputAudio,
    InputAudioChatCompletionContentPart,

    RefusalChatCompletionContentPart,

    ChatCompletionContentPart,
)

from .chatcompletion.message import (  # noqa
    DeveloperChatCompletionMessage,

    SystemChatCompletionMessage,

    UserChatCompletionMessage,

    AssistantChatCompletionMessageAudio,
    AssistantChatCompletionMessageToolCallFunction,
    AssistantChatCompletionMessageToolCall,
    AssistantChatCompletionMessage,

    ToolChatCompletionMessage,

    FunctionChatCompletionMessage,

    ChatCompletionMessage,
)

from .chatcompletion.request import (  # noqa
    ChatCompletionRequestWebSearchOptionsUserLocationApproximate,
    ChatCompletionRequestWebSearchOptionsUserLocation,
    ChatCompletionRequestWebSearchOptions,

    ChatCompletionRequestPrediction,

    ChatCompletionRequestToolFunction,
    ChatCompletionRequestTool,

    ChatCompletionRequestStreamOptions,

    ChatCompletionRequestNamedToolChoiceFunction,
    ChatCompletionRequestNamedToolChoice,

    ChatCompletionRequestAudio,

    ChatCompletionRequest,
)

from .chatcompletion.response import (  # noqa
    ChatCompletionResponseAnnotationUrlCitation,
    ChatCompletionResponseAnnotation,

    ChatCompletionResponseAudio,

    ChatCompletionResponseMessageToolCallFunction,
    ChatCompletionResponseMessageToolCall,
    ChatCompletionResponseMessage,

    ChatCompletionResponseChoiceLogprobs,
    ChatCompletionResponseChoice,

    ChatCompletionResponse,
)

from .chatcompletion.responseformat import (  # noqa
    TextChatCompletionResponseFormat,

    JsonSchemaChatCompletionResponseFormatJsonSchema,
    JsonSchemaChatCompletionResponseFormat,

    JsonObjectChatCompletionResponseFormat,

    ChatCompletionResponseFormat,
)

from .chatcompletion.tokenlogprob import (  # noqa
    ChatCompletionTokenLogprobTopLogprob,
    ChatCompletionTokenLogprob,
)

from .completionusage import (  # noqa
    CompletionUsageCompletionTokensDetails,
    CompletionUsagePromptTokensDetails,
    CompletionUsage,
)
