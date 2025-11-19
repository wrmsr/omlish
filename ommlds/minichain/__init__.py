# fmt: off
# ruff: noqa: I001
from omlish import dataclasses as _dc  # noqa


_dc.init_package(
    globals(),
    codegen=True,
)


##


from omlish import lang as _lang  # noqa


with _lang.auto_proxy_init(
        globals(),
        # disable=True,
        # eager=True,
):
    ##

    from .backends.catalogs.base import (  # noqa
        BackendCatalog,
    )

    from .backends.catalogs.simple import (  # noqa
        SimpleBackendCatalogEntry,
        SimpleBackendCatalogEntries,

        SimpleBackendCatalog,

        simple_backend_catalog_entry,
    )

    from .backends.catalogs.strings import (  # noqa
        BackendStringBackendCatalog,
    )

    from .backends.strings.manifests import (  # noqa
        BackendStringsManifest,
    )

    from .backends.strings.parsing import (  # noqa
        ParsedBackendString,

        parse_backend_string,
    )

    from .backends.strings.resolving import (  # noqa
        ResolveBackendStringArgs,
        ResolveBackendStringResult,
        AmbiguousBackendStringResolutionError,
        BackendStringResolver,

        CompositeBackendStringResolver,
        FirstCompositeBackendStringResolver,
        UniqueCompositeBackendStringResolver,
        ManifestBackendStringResolver,

        build_manifest_backend_string_resolver,
    )

    ##

    from .chat.choices.stream.adapters import (  # noqa
        ChatChoicesStreamServiceChatChoicesService,
    )

    from .chat.choices.stream.joining import (  # noqa
        AiChoicesDeltaJoiner,
    )

    from .chat.choices.stream.services import (  # noqa
        ChatChoicesStreamRequest,
        ChatChoicesStreamResponse,
        ChatChoicesStreamService,
        AbstractChatChoicesStreamService,
        static_check_is_chat_choices_stream_service,
    )

    from .chat.choices.stream.types import (  # noqa
        ChatChoicesStreamOption,
        ChatChoicesStreamOptions,

        ChatChoicesStreamOutput,
        ChatChoicesStreamOutputs,

        AiChoiceDeltas,
        AiChoicesDeltas,
    )

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

    from .chat.stream.joining import (  # noqa
        AiDeltaJoiner,
    )

    from .chat.stream.services import (  # noqa
        ChatStreamRequest,
        ChatStreamResponse,
        ChatStreamService,
        AbstractChatStreamService,
        static_check_is_chat_stream_service,
    )

    from .chat.stream.types import (  # noqa
        AiDelta,
        AiDeltas,

        ContentAiDelta,

        AnyToolUseAiDelta,
        ToolUseAiDelta,
        PartialToolUseAiDelta,
    )

    from .chat.tools.execution import (  # noqa
        execute_tool_use,
    )

    from .chat.transforms.base import (  # noqa
        MessageTransform,
        CompositeMessageTransform,
        FnMessageTransform,
        TypeFilteredMessageTransform,

        ChatTransform,
        CompositeChatTransform,
        FnChatTransform,

        MessageTransformChatTransform,
        LastMessageTransformChatTransform,
    )

    from .chat.transforms.metadata import (  # noqa
        UuidAddingMessageTransform,
        CreatedAtAddingMessageTransform,
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
        Message,
        Chat,

        AnyUserMessage,
        UserChat,
        check_user_chat,

        AnyAiMessage,
        AiChat,
        check_ai_chat,

        SystemMessage,
        UserMessage,
        AiMessage,
        ToolUseMessage,
        ToolUseResultMessage,
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

    from .chat.tools.types import (  # noqa
        Tool,
    )

    from .chat.types import (  # noqa
        ChatOption,
        ChatOptions,

        ChatOutput,
        ChatOutputs,
    )

    ##

    from .content.images import (  # noqa
        ImageContent,
    )

    from .content.json import (  # noqa
        JsonContent,
    )

    from .content.materialize import (  # noqa
        CanContent,

        materialize_content,
    )

    from .content.metadata import (  # noqa
        ContentMetadata,
        ContentMetadatas,
    )

    from .content.namespaces import (  # noqa
        ContentNamespace,
    )

    from .content.placeholders import (  # noqa
        ContentPlaceholder,
        ContentPlaceholderMarker,
        content_placeholder,
    )

    from .content.prepare import (  # noqa
        ContentPreparer,
        ContentStrPreparer,

        DefaultContentPreparer,
        DefaultContentStrPreparer,

        default_content_preparer,
        default_content_str_preparer,
        prepare_content,
        prepare_content_str,
    )

    from .content.sequence import (  # noqa
        BlockContent,
        InlineContent,
        SequenceContent,
    )

    from .content.text import (  # noqa
        TextContent,
    )

    from .content.transforms.base import (  # noqa
        ContentTransform,
    )

    from .content.types import (  # noqa
        Content,
        ExtendedContent,
        SingleContent,
        SingleExtendedContent,
    )

    from .content.transforms.strings import (  # noqa
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

    from .models.repos.resolving import (  # noqa
        ResolvedModelRepo,
        ModelRepoResolver,
    )

    from .models.configs import (  # noqa
        ModelSpecifier,
        ModelName,
        ModelPath,
        ModelRepo,
    )

    from .models.names import (  # noqa
        ModelNameCollection,
    )

    ##

    from .registries.globals import (  # noqa
        get_registry_cls,
        register_type,
        registry_new,
        registry_of,
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

    from .stream.services import (  # noqa
        StreamOption,
        StreamOptions,

        StreamResponseSink,
        StreamResponseIterator,

        StreamServiceCancelledError,
        StreamServiceNotAwaitedError,

        StreamResponse,
        new_stream_response,
    )

    from .stream.wrap import (  # noqa
        WrappedStreamService,
    )

    ##

    from .tools.execution.catalog import (  # noqa
        ToolCatalogEntry,
        ToolCatalogEntries,
        ToolCatalog,
    )

    from .tools.execution.context import (  # noqa
        ToolContext,

        bind_tool_context,
        tool_context,
    )

    from .tools.execution.executors import (  # noqa
        ToolExecutor,

        ToolFnToolExecutor,

        NameSwitchedToolExecutor,
    )

    from .tools.execution.reflect import (  # noqa
        reflect_tool_catalog_entry,
    )

    from .tools.execution.errors import (  # noqa
        ToolExecutionError,
    )

    from .tools.fns import (  # noqa
        ToolFn,

        execute_tool_fn,
    )

    from .tools.jsonschema import (  # noqa
        build_tool_spec_json_schema,
    )

    from .tools.reflect import (  # noqa
        tool_spec_attach,
        tool_spec_override,
        tool_param_metadata,

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

        ToolUse,
        ToolUseResult,
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

    from .json import (  # noqa
        JsonSchema,

        JsonValue,
    )

    from .metadata import (  # noqa
        Metadata,

        MetadataContainer,

        CommonMetadata,
        Uuid,
        CreatedAt,
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
        Device,

        ApiUrl,

        ApiKey,

        DefaultOptions,
    )

    from .types import (  # noqa
        Option,

        Output,
    )
