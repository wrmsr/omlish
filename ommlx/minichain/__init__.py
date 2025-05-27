# fmt: off

from .backends.manifests import (  # noqa
    backend_of,
    new_backend,
)

from .chat.formats import (  # noqa
    JSON_RESPONSE_FORMAT,
    JsonResponseFormat,
    ResponseFormat,
    TEXT_RESPONSE_FORMAT,
    TextResponseFormat,
)

from .chat.history import (  # noqa
    ChatHistory,
    ChatHistoryService,
    ListChatHistory,
)

from .chat.messages import (  # noqa
    AiMessage,
    Chat,
    Message,
    SystemMessage,
    ToolExecResultMessage,
    UserMessage,
)

from .chat.choices import (  # noqa
    AiChoice,
    AiChoices,
)

from .chat.services import (  # noqa
    ChatRequest,
    ChatResponse,
    ChatService,
    ChatService_,
)

from .chat.streaming import (  # noqa
    ChatStreamRequest,
    ChatStreamResponse,

    ChatStreamService,
    ChatStreamService_,
)

from .chat.templating import (  # noqa
    ChatTemplatePart,
    ChatTemplate,

    MessageTemplate,
    MessagePlaceholder,

    ChatTemplater,
)

from .chat.tools import (  # noqa
    Tool,
)

from .chat.types import (  # noqa
    ChatRequestOption,
    ChatResponseOutput,
)

from .completion import (  # noqa
    CompletionRequest,
    CompletionRequestOption,
    CompletionResponse,
    CompletionResponseOutput,
    CompletionService,
)

from .configs import (  # noqa
    Config,

    consume_configs,
)

from .content.content import (  # noqa
    Content,
    ExtendedContent,
)

from .content.images import (  # noqa
    Image,
)

from .content.rendering import (  # noqa
    StringRenderer,
)

from .content.transforms import (  # noqa
    ContentTransform,

    StringFnContentTransform,
    transform_content_strings,
)

from .envs import (  # noqa
    Env,
    EnvKey,
)

from .llms.tokens import (  # noqa
    Token,
    Tokens,
)

from .llms.services import (  # noqa
    LlmRequestOption,

    TopK,
    Temperature,
    MaxTokens,

    LlmResponseOutput,

    FinishReason,
    FinishReasonOutput,

    TokenUsage,
    TokenUsageOutput,
)

from .services import (  # noqa
    Request,
    RequestOption,
    Response,
    ResponseOutput,
    Service,
    Service_,
)

from .standard import (  # noqa
    ModelSpecifier,
    ModelName,
    ModelPath,

    ApiKey,

    DefaultRequestOptions,
)

from .streaming import (  # noqa
    StreamResponse,
)

from .tools.jsonschema import (  # noqa
    build_tool_spec_json_schema,
)

from .tools.reflection import (  # noqa
    reflect_tool_spec,
)

from .tools.types import (  # noqa
    ToolDtype,

    PrimitiveToolDtype,

    UnionToolDtype,
    NullableToolDtype,

    SequenceToolDtype,
    MappingToolDtype,
    TupleToolDtype,

    EnumToolDtype,

    ToolParam,

    ToolSpec,

    ToolExecRequest,
)

from .vectors.embeddings import (  # noqa
    EmbeddingRequest,
    EmbeddingRequestOption,
    EmbeddingResponse,
    EmbeddingResponseOutput,
    EmbeddingService,
)

from .vectors.index import (  # noqa
    VectorIndexRequest,
    VectorIndexRequestOption,
    VectorIndexResponse,
    VectorIndexResponseOutput,
    VectorIndexService,
    VectorIndexed,
)

from .vectors.search import (  # noqa
    VectorHit,
    VectorHits,
    VectorSearch,
    VectorSearchRequest,
    VectorSearchRequestOption,
    VectorSearchResponse,
    VectorSearchResponseOutput,
    VectorSearchService,
    VectorSearchSimilarity,
)

from .vectors.similarity import (  # noqa
    CALC_NP_SIMILARITIES_FUNCS,
    Similarity,
    calc_np_cosine_similarities,
    calc_np_dot_similarities,
    calc_np_similarities,
)

from .vectors.stores import (  # noqa
    VectorStore,
)

from .vectors.types import (  # noqa
    Vector,
    Vectorable,
)


##


from omlish.lang.imports import _register_conditional_import  # noqa

_register_conditional_import('omlish.marshal', '.chat.marshal', __package__)
_register_conditional_import('omlish.marshal', '.content.marshal', __package__)
_register_conditional_import('omlish.marshal', '.llms.marshal', __package__)
_register_conditional_import('omlish.marshal', '.tools.marshal', __package__)
