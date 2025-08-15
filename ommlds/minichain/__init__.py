# fmt: off
from omlish import lang as _lang


with _lang.auto_proxy_init(
        globals(),
        # disable=True,
        # eager=True,
):
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

    from .chat.tools.execution import (  # noqa
        m_execute_tool_request,
    )

    from .chat.transforms.base import (  # noqa
        MessageTransform,
        CompositeMessageTransform,
        FnMessageTransform,
        TypeFilteredMessageTransform,
        fn_message_transform,

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

    from .content.materialize import (  # noqa
        CanContent,
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

    from .models.configs import (  # noqa
        ModelSpecifier,
        ModelName,
        ModelPath,
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

        ResponseGenerator,
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

    from .tools.fns import (  # noqa
        ToolFn,

        m_execute_tool_fn,
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
        CreatedAt,
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
        ApiKey,

        DefaultOptions,
    )

    from .types import (  # noqa
        Option,

        Output,
    )
