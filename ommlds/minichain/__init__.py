# fmt: off

##

from .chat.choices.adapters import (  # noqa
    ChatChoicesServiceChatService,
)

from .chat.choices.services import (  # noqa
    ChatChoicesRequest,
    ChatChoicesResponse,
    ChatChoicesService,
    AbstractChatChoicesService,
    static_check_is_chat_choices_service,
)

from .chat.choices.types import (  # noqa
    ChatChoicesOption,
    ChatChoicesOptions,

    ChatChoicesOutput,
    ChatChoicesOutputs,

    AiChoice,
    AiChoices,
)

from .chat.stream.adapters import (  # noqa
    ChatChoicesStreamServiceChatChoicesService,
)

from .chat.stream.services import (  # noqa
    ChatChoicesStreamRequest,
    ChatChoicesStreamResponse,
    ChatChoicesStreamService,
    AbstractChatChoicesStreamService,
    static_check_is_chat_choices_stream_service,

    ChatChoicesStreamGenerator,
)

from .chat.stream.types import (  # noqa
    ChatChoicesStreamOption,
    ChatChoicesStreamOptions,

    ChatChoicesStreamOutput,
    ChatChoicesStreamOutputs,

    ToolExecRequestDelta,
    AiMessageDelta,
    AiChoiceDelta,
    AiChoiceDeltas,
)

from .chat.transforms.base import (  # noqa
    MessageTransform,

    ChatTransform,

    MessageTransformChatTransform,
)

from .chat.transforms.uuids import (  # noqa
    UuidAddingMessageTransform,
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
    ListChatHistory,

    HistoryAddingChatService,
)

from .chat.messages import (  # noqa
    AiMessage,
    Chat,
    Message,
    SystemMessage,
    ToolExecResultMessage,
    UserMessage,
)

from .chat.services import (  # noqa
    ChatRequest,
    ChatResponse,
    ChatService,
    AbstractChatService,
    static_check_is_chat_service,
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
    ChatOption,
    ChatOptions,

    ChatOutput,
    ChatOutputs,
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

from .llms.types import (  # noqa
    LlmOption,

    TopK,
    Temperature,
    MaxTokens,

    LlmOutput,

    FinishReason,
    FinishReasonOutput,

    TokenUsage,
    TokenUsageOutput,
)

##

from .services import (  # noqa
    Request,
    Response,
    Service,
    ServiceFacade,
    facade,
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
    EmbeddingOption,
    EmbeddingOptions,

    EmbeddingOutput,
    EmbeddingOutputs,

    EmbeddingRequest,
    EmbeddingResponse,
    EmbeddingService,
    static_check_is_embedding_service,
)

from .vectors.index import (  # noqa
    VectorIndexed,

    VectorIndexOption,
    VectorIndexOptions,

    VectorIndexOutput,
    VectorIndexOutputs,

    VectorIndexRequest,
    VectorIndexResponse,
    VectorIndexService,
    static_check_is_vector_index_service,
)

from .vectors.search import (  # noqa
    VectorSearch,
    VectorHit,
    VectorHits,

    VectorSearchOption,
    VectorSearchOptions,

    VectorSearchOutput,
    VectorSearchSimilarity,
    VectorSearchOutputs,

    VectorSearchRequest,
    VectorSearchResponse,
    VectorSearchService,
    static_check_is_vector_search_service,
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
    CompletionOption,
    CompletionOptions,

    CompletionOutput,
    CompletionOutputs,

    CompletionRequest,
    CompletionResponse,
    CompletionService,
    static_check_is_completion_service,
)

from .configs import (  # noqa
    Config,
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

    ResourcesOption,
    UseResources,
)

from .search import (  # noqa
    SearchOption,
    SearchOptions,

    SearchOutput,
    SearchOutputs,

    SearchRequest,
    SearchResponse,
    SearchService,
    static_check_is_search_service,
)

from .standard import (  # noqa
    ModelSpecifier,
    ModelName,
    ModelPath,

    ApiKey,

    DefaultOptions,
)

from .stream.services import (  # noqa
    StreamOption,
    StreamOptions,

    ResponseGenerator,
    StreamResponse,
    new_stream_response,
)

from .stream.wrap import (  # noqa
    WrappedStreamService,
)

from .types import (  # noqa
    Option,

    Output,
)


##


from omlish.lang.imports import _register_conditional_import  # noqa

_register_conditional_import('omlish.marshal', '.chat._marshal', __package__)
_register_conditional_import('omlish.marshal', '.content._marshal', __package__)
_register_conditional_import('omlish.marshal', '.llms._marshal', __package__)
_register_conditional_import('omlish.marshal', '.tools._marshal', __package__)
