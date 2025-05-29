"""
https://github.com/langchain4j/langchain4j/tree/d069798d52430203084dcb2114cbbd3afc3ff6cb/langchain4j-core/src/main/java/dev/langchain4j

==

agent
  tool
    JsonSchemaProperty
    P
    Tool
    ToolExecutionRequest
    ToolMemoryId
    ToolParameters
    ToolSpecification
    ToolSpecifications

code
  CodeExecutionEngine

data
  audio
    Audio

  document
    BlankDocumentException
    Document
    DocumentLoader
    DocumentParser
    DocumentSource
    DocumentSplitter
    DocumentTransformer
    Metadata

  embedding
    Embedding

  image
    Image

  message
    AiMessage
    AudioContent
    ChatMessage
    ChatMessageDeserializer
    ChatMessageJsonCodec
    ChatMessageSerializer
    ChatMessageType
    Content
    ContentType
    GsonChatMessageAdapter
    GsonChatMessageJsonCodec
    GsonContentAdapter
    ImageContent
    PdfFileContent
    SystemMessage
    TextContent
    TextFileContent
    ToolExecutionResultMessage
    UserMessage
    VideoContent

  pdf
    PdfFile

  segment
    TextSegment
    TextSegmentTransformer

  text
    TextFile

  video
    Video

internal
  CustomMimeTypesFileTypeDetector
  Exceptions
  GsonJsonCodec
  JacocoIgnoreCoverageGenerated
  Json
  RetryUtils
  TypeUtils
  Utils
  ValidationUtils

memory
  ChatMemory

model
  chat
    listener
      ChatModelErrorContext
      ChatModelListener
      ChatModelRequest
      ChatModelRequestContext
      ChatModelResponse
      ChatModelResponseContext

    request
      json
        JsonArraySchema
        JsonBooleanSchema
        JsonEnumSchema
        JsonIntegerSchema
        JsonNumberSchema
        JsonObjectSchema
        JsonSchema
        JsonSchemaElement
        JsonStringSchema

      ChatRequest
      ResponseFormat
      ResponseFormatType

    response
      ChatResponse

    Capability
    ChatLanguageModel
    DisabledChatLanguageModel
    DisabledStreamingChatLanguageModel
    StreamingChatLanguageModel
    TokenCountEstimator

  embedding
    DimensionAwareEmbeddingModel
    DisabledEmbeddingModel
    EmbeddingModel
    TokenCountEstimator

  image
    DisabledImageModel
    ImageModel

  input
    structured
      DefaultStructuredPromptFactory
      StructuredPrompt
      StructuredPromptProcessor

    DefaultPromptTemplateFactory
    Prompt
    PromptTemplate

  language
    DisabledLanguageModel
    DisabledStreamingLanguageModel
    LanguageModel
    StreamingLanguageModel
    TokenCountEstimator

  moderation
    DisabledModerationModel
    Moderation
    ModerationModel

  output
    structured
      Description

    FinishReason
    Response
    TokenUsage

  scoring
    ScoringModel

  LambdaStreamingResponseHandler
  ModelDisabledException
  StreamingResponseHandler
  Tokenizer

rag
  content
    aggregator
      ContentAggregator
      DefaultContentAggregator
      ReRankingContentAggregator
      ReciprocalRankFuser

    injector
      ContentInjector
      DefaultContentInjector

    retriever
      ContentRetriever
      EmbeddingStoreContentRetriever
      WebSearchContentRetriever

    Content

  query
    router
      DefaultQueryRouter
      LanguageModelQueryRouter
      QueryRouter

    transformer
      CompressingQueryTransformer
      DefaultQueryTransformer
      ExpandingQueryTransformer
      QueryTransformer

    Metadata
    Query

  AugmentationRequest
  AugmentationResult
  DefaultRetrievalAugmentor
  RetrievalAugmentor

retriever
  EmbeddingStoreRetriever
  Retriever

spi
  ServiceHelper
  data
    document
      parser
        DocumentParserFactory
      splitter
        DocumentSplitterFactory
    message
      ChatMessageJsonCodecFactory
  json
    JsonCodecFactory
  model
    embedding
      EmbeddingModelFactory
  prompt
    PromptTemplateFactory
    structured
      StructuredPromptFactory

store
  embedding
    filter
      comparison
        IsEqualTo
        IsGreaterThan
        IsGreaterThanOrEqualTo
        IsIn
        IsLessThan
        IsLessThanOrEqualTo
        IsNotEqualTo
        IsNotIn
        NumberComparator
        TypeChecker
        UUIDComparator

      logical
        And
        Not
        Or

      Filter
      FilterParser
      MetadataFilterBuilder

    CosineSimilarity
    EmbeddingMatch
    EmbeddingSearchRequest
    EmbeddingSearchResult
    EmbeddingStore
    EmbeddingStoreIngestor
    RelevanceScore

  memory
    chat
      ChatMemoryStore
      InMemoryChatMemoryStore

web
  search
    WebSearchEngine
    WebSearchInformationResult
    WebSearchOrganicResult
    WebSearchRequest
    WebSearchResults
    WebSearchTool
"""
