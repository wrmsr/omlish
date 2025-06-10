# fmt: off

##

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
    ChatRequestOption,
    ChatRequestOptions,
    ChatRequest,

    ChatResponseOutput,
    ChatResponseOutputs,
    ChatResponse,

    ChatService,
)

from .chat.streaming import (  # noqa
    ChatStreamResponse,

    ChatStreamService,
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

##

from .content.content import (  # noqa
    Content,
    ExtendedContent,
)

from .content.images import (  # noqa
    ImageContent,
)

from .content.list import (  # noqa
    ListContent,
)

from .content.metadata import (  # noqa
    ContentMetadata,
    ContentMetadatas,
)

from .content.rendering import (  # noqa
    StringRenderer,
)

from .content.text import (  # noqa
    TextContent,
)

from .content.transforms import (  # noqa
    ContentTransform,

    StringFnContentTransform,
    transform_content_strings,
)

##

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

##

from .services import (  # noqa
    Request,
    RequestOption,
    Response,
    ResponseOutput,
    Service,
    ServiceFacade,
)

##

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

##

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

from .completion import (  # noqa
    CompletionRequestOption,
    CompletionRequestOptions,
    CompletionRequest,

    CompletionResponseOutput,
    CompletionResponseOutputs,
    CompletionResponse,

    CompletionService,
)

from .configs import (  # noqa
    Config,

    consume_configs,
)

from .envs import (  # noqa
    Env,
    EnvKey,
)

from .metadata import (  # noqa
    Metadata,

    MetadataContainer,

    CommonMetadata,

    Uuid,
)

from .registry import (  # noqa
    register_type,
    registry_new,
    registry_of,
)

from .resources import (  # noqa
    ResourcesRef,
    ResourcesRefNotRegisteredError,
    Resources,

    ResourceManaged,
)

from .standard import (  # noqa
    ModelSpecifier,
    ModelName,
    ModelPath,

    ApiKey,

    DefaultRequestOptions,
)

from .streaming import (  # noqa
    ResponseGenerator,

    StreamResponse,
)


##


from omlish.lang.imports import _register_conditional_import  # noqa

_register_conditional_import('omlish.marshal', '.chat._marshal', __package__)
_register_conditional_import('omlish.marshal', '.content._marshal', __package__)
_register_conditional_import('omlish.marshal', '.llms._marshal', __package__)
_register_conditional_import('omlish.marshal', '.tools._marshal', __package__)
