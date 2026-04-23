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

    from .chat.transform.types import (  # noqa
        MessageTransform,

        CompositeMessageTransform,
        FnMessageTransform,
        TypeFilteredMessageTransform,

        ChatTransform,

        CompositeChatTransform,
        FnChatTransform,
        MessageTransformChatTransform,
    )

    from .chat.transform.content import (  # noqa
        ContentTransformMessageTransform,
    )

    from .chat.transform.metadata import (  # noqa
        CreatedAtAddingMessageTransform,
        MessageUuidAddingMessageTransform,
        TurnUuidAddingMessageTransform,
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
        DeveloperMessage,
        UserMessage,
        AiMessage,
        ToolUseMessage,
        ToolUseResultMessage,
    )

    from .chat.metadata import (  # noqa
        MessageMetadata,
        MessageMetadatas,

        MessageUuid,
        TurnUuid,
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

    from .content.render.standard import (  # noqa
        StandardContentRenderer,

        render_content_str,
    )

    from .content.render.types import (  # noqa
        ContentRenderer,
        ContentStrRenderer,
    )

    ##

    from .content.transform.materialize.placeholders import (  # noqa
        PlaceholderContentKeyError,
        MissingPlaceholderContentKeyError,
        DuplicatePlaceholderContentKeyError,
    )

    from .content.transform.strings import (  # noqa
        StringFnContentTransform,
        transform_content_strings,
    )

    from .content.transform.types import (  # noqa
        ContentTransform,

        CompositeContentTransform,
        FnContentTransform,
        TypeFilteredContentTransform,
    )

    from .content.transform.visitors import (  # noqa
        VisitorContentTransform,
    )

    ##

    from .content.blank import (  # noqa
        BlankContent,
    )

    from .content.code import (  # noqa
        CodeContent,
        InlineCodeContent,
        BlockCodeContent,
    )

    from .content.composite import (  # noqa
        CompositeContent,
    )

    from .content.containers import (  # noqa
        ContainerContent,
        FlowContent,
        ConcatContent,
        BlocksContent,
    )

    from .content.content import (  # noqa
        ContentBase,

        Content,
        CONTENT_TYPES,
    )

    from .content.dynamic import (  # noqa
        DynamicContent,
    )

    from .content.emphasis import (  # noqa
        BoldContent,
        ItalicContent,
        BoldItalicContent,
    )

    from .content.images import (  # noqa
        ImageContent,
    )

    from .content.itemlist import (  # noqa
        ItemListContent,
    )

    from .content.json import (  # noqa
        JsonContent,
    )

    from .content.link import (  # noqa
        LinkContent,
    )

    from .content.markdown import (  # noqa
        MarkdownContent,
    )

    from .content.metadata import (  # noqa
        ContentMetadata,
        ContentMetadatas,

        ContentUuid,

        ContentOriginal,
    )

    from .content.namespaces import (  # noqa
        ContentNamespace,
        NamespaceContent,
    )

    from .content.placeholders import (  # noqa
        ContentPlaceholder,
        PlaceholderContentKey,
        PlaceholderContent,

        PlaceholderContentValue,
        PlaceholderContentMap,
        PlaceholderContents,
    )

    from .content.quote import (  # noqa
        QuoteContent,
    )

    from .content.raw import (  # noqa
        NonStrSingleRawContent,
        NON_STR_SINGLE_RAW_CONTENT_TYPES,

        SingleRawContent,
        SINGLE_RAW_CONTENT_TYPES,

        RawContent,
        RAW_CONTENT_TYPES,
    )

    from .content.recursive import (  # noqa
        RecursiveContent,
    )

    from .content.resources import (  # noqa
        ResourceContent,
        resource_content,
    )

    from .content.section import (  # noqa
        SectionContent,
    )

    from .content.sequence import (  # noqa
        SequenceContent,
    )

    from .content.standard import (  # noqa
        StandardContent,
    )

    from .content.tag import (  # noqa
        TagContent,
    )

    from .content.templates import (  # noqa
        TemplateContent,
    )

    from .content.text import (  # noqa
        TextContent,
    )

    from .content.visitors import (  # noqa
        ContentVisitor,

        StandardContentVisitorTypeError,
        StandardContentVisitor,

        StaticContentVisitorTypeError,
        StaticContentVisitor,
    )

    ##

    from . import drivers  # noqa

    ##

    from . import facades  # noqa

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
        MaxCompletionTokens,

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

    from . import modules  # noqa

    ##

    from .registries.globals import (  # noqa
        get_registry_cls,
        register_type,
        registry_new,
        registry_of,
    )

    from .registries.registry import (  # noqa
        RegistryTypeName,
        registry_type_repr,

        Registry,
    )

    ##

    from .services import (  # noqa
        #

        ServiceFacade,
        facade,

        #

        ReflectedService,
        ReflectedStreamService,

        reflect_service_like,
        reflect_service_cls,

        is_stream_service_cls,

        #

        RequestMetadata,
        RequestMetadatas,
        Request,

        #

        ResponseMetadata,
        ResponseMetadatas,
        Response,

        #

        Service,

        #

        StreamOption,
        StreamOptions,

        StreamResponseSink,
        StreamResponseIterator,

        StreamServiceCancelledError,
        StreamServiceNotAwaitedError,

        StreamResponse,
        new_stream_response,

        #

        WrappedRequestV,
        WrappedOptionT,
        WrappedResponseV,
        WrappedOutputT,
        WrappedStreamOutputT,

        WrappedRequest,
        WrappedResponse,
        WrappedService,

        WrappedStreamOptions,
        WrappedStreamRequest,
        WrappedStreamResponse,
        WrappedStreamService,

        WrapperService,
        MultiWrapperService,

        WrapperStreamService,
        MultiWrapperStreamService,

        wrap_service,
    )

    ##

    from .tools.execution.catalog import (  # noqa
        ToolCatalogEntry,
        ToolCatalogEntries,
        ToolCatalog,
    )

    from .tools.execution.context import (  # noqa
        ToolContextKeyError,
        ToolContext,

        bind_tool_context,
        tool_context,
    )

    from .tools.execution.errorhandling import (  # noqa
        ErrorHandlingToolExecutor,
    )

    from .tools.execution.errors import (  # noqa
        ToolExecutionError,
        PermissionDeniedToolExecutionError,
    )

    from .tools.execution.executors import (  # noqa
        ToolExecutor,

        ToolFnToolExecutor,

        NameSwitchedToolExecutor,
    )

    from .tools.execution.permissions import (  # noqa
        DecidedToolPermissionState,
        ToolPermissionDecider,
        StaticToolPermissionDecider,

        tool_permission_decider,
    )

    from .tools.execution.reflect import (  # noqa
        reflect_tool_catalog_entry,
    )

    from .tools.permissions.bash import (  # noqa
        BashToolPermissionTarget,
        BashToolPermissionMatcher,
    )

    from .tools.permissions.collection import (  # noqa
        ToolPermissionRules,
    )

    from .tools.permissions.fs import (  # noqa
        FsToolPermissionMode,

        FsToolPermissionTarget,
        GlobFsToolPermissionMatcher,
    )

    from .tools.permissions.managers import (  # noqa
        ToolPermissionsManager,
        SimpleToolPermissionsManager,
    )

    from .tools.permissions.types import (  # noqa
        ToolPermissionState,

        ToolPermissionTarget,

        ToolPermissionMatcher,

        ToolPermissionRule,
    )

    from .tools.permissions.url import (  # noqa
        UrlToolPermissionTarget,
        RegexUrlToolPermissionMatcher,
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

    from .wrappers.metadata import (  # noqa
        RetryServiceResponseMetadata,
    )

    from .wrappers.retry import (  # noqa
        AnyRetryService,

        RetryServiceMaxRetriesExceededError,

        RetryService,

        RetryStreamService,
    )

    from .wrappers.uuids import (  # noqa
        RequestResponseUuidAddingService,
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

        CreatedAt,

        RequestUuid,
        ParentRequestUuid,
        ResponseUuid,
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
    )

    from .types import (  # noqa
        Option,

        Output,
    )


##


from omlish import marshal as _msh  # noqa

_msh.register_global_module_import('._marshal', __package__)
