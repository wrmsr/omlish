- handler tags, tracing / debug
- struct opts - simultaneously both marshal/unmarshal
- containers
- identities / objgraphs
- 'auto-hierarchy' - default polymorphism tags
- 'auto-factory' - arg names / types correspond to fields
    - correlate with getters
- timed or nth accessed CoW cached type map
- register warming types
- case folding impl on ctxs
- type-switched polymorphic - if only impls are a userstring and userint
- enum default omission
- inject interop

- ! streaming
- (json) schematizing
- afterburner: codegen, verify at boot?

- mapstruct:
    - ErrorUnused - If ErrorUnused is true, then it is an error for there to exist keys in the original map that were
      unused in the decoding process (extra keys).
    - ErrorUnset - If ErrorUnset is true, then it is an error for there to exist fields in the result that were not set
      in the decoding process (extra fields). This only applies to decoding to a struct. This/ will affect all nested
      structs as well.
    - ZeroFields - ZeroFields, if set to true, will zero fields before writing them. For example, a map will be emptied
      before decoded values are put in it. If this is false, a map will be merged.
    - WeaklyTypedInput - If WeaklyTypedInput is true, the decoder will make the following "weak" conversions:
        - bools to string (true = "1", false = "0")
        - numbers to string (base 10)
        - bools to int/uint (true = 1, false = 0)
        - strings to int/uint (base implied by prefix)
        - int to bool (true if value != 0)
        - string to bool (accepts: 1, t, T, TRUE, true, True, 0, f, F, FALSE, false, False. Anything else is an error)
        - empty array = empty map and vice versa
        - negative numbers to overflowed uint values (base 10)
        - slice of maps to a merged map
        - single values are converted to slices if required. Each element is weakly decoded. For example: "4" can
          become []int{4} if the target type is an int slice.
    - Squash - Squash will squash embedded structs. A squash tag may also be added to an individual struct field using a
      tag. For example: type Parent struct { Child `mapstructure:",squash"` }
    - Metadata - Metadata is the struct that will contain extra metadata about the decoding. If this is nil, then no
      metadata will be tracked.
    - TagName - The tag name that mapstructure reads for field names. This defaults to "mapstructure"
    - IgnoreUntaggedFields - IgnoreUntaggedFields ignores all struct fields without explicit TagName, comparable
      to `mapstructure:"-"` as default behaviour.
    - MatchName - MatchName is the function used to match the map key to the struct field name or tag. Defaults
      to `strings.EqualFold`. This can be used to implement case-sensitive tag values, support snake casing, etc.

- poly
    - embedding inheritance

- jackson
  - core annotations
    - Property Naming
      - @JsonProperty
      - @JsonProperty.value
      - @JsonProperty.index
      - @JsonProperty.defaultValue
    - Property Inclusion
      - @JsonAutoDetect
        - creatorVisibility
        - fieldVisibility
        - getterVisibility
        - isGetterVisibility
        - setterVisibility
          - ANY
          - NON_PRIVATE
          - PROTECTED_AND_PUBLIC
          - PUBLIC_ONLY
          - NONE
          - DEFAULT
      - @JsonIgnore
      - @JsonIgnoreProperties
      - @JsonIgnoreType
      - @JsonInclude
      - @JsonPropertyDescription
    - Deserialization and Serialization details
      - @JsonFormat
        - lenient
        - locale
        - pattern
        - shape
        - timezone
        - with
        - without
      - @JsonUnwrapped
      - @JsonView
    - Deserialization details
      - @JacksonInject
      - @JsonAnySetter
      - @JsonCreator
      - @JsonSetter
      - @JsonEnumDefaultValue
    - Serialization details
      - @JsonAnyGetter
      - @JsonGetter
      - @JsonPropertyOrder
      - @JsonRawValue
      - @JsonValue
      - @JsonRootName
    - Type handling
      - @JsonSubTypes
      - @JsonTypeId
      - @JsonTypeInfo
      - @JsonTypeName
    - Object references, identity
      - @JsonManagedReference, @JsonBackReference
      - @JsonIdentityInfo
    - Meta-annotations
      - @JacksonAnnotation
      - @JacksonAnnotationsInside
      - @JsonView
      - @JsonRootName
      - @JacksonAnnotationsInside
      - @JacksonFeature
  - streaming factory features
    - Name canonicalization
      - CANONICALIZE_FIELD_NAMES
      - INTERN_FIELD_NAMES
      - FAIL_ON_SYMBOL_HASH_OVERFLOW
      - USE_THREAD_LOCAL_FOR_BUFFER_RECYCLING
  - stream read features
    - Low-level I/O handling features
      - AUTO_CLOSE_SOURCE
    - Additional input validation
      - STRICT_DUPLICATE_DETECTION
      - IGNORE_UNDEFINED
    - Misc Other
      - INCLUDE_SOURCE_IN_LOCATION
      - USE_FAST_DOUBLE_PARSER
  - json read features
    - Support for non-standard JSON content (deviations from JSON specification)
      - ALLOW_JAVA_COMMENTS
      - ALLOW_YAML_COMMENTS
      - ALLOW_SINGLE_QUOTES
      - ALLOW_UNQUOTED_FIELD_NAMES
      - ALLOW_UNESCAPED_CONTROL_CHARS
      - ALLOW_BACKSLASH_ESCAPING_ANY_CHARACTER
      - ALLOW_LEADING_ZEROS_FOR_NUMBERS
      - ALLOW_LEADING_PLUS_SIGN_FOR_NUMBERS
      - ALLOW_LEADING_DECIMAL_POINT_FOR_NUMBERS
      - ALLOW_TRAILING_DECIMAL_POINT_FOR_NUMBERS
      - ALLOW_NON_NUMERIC_NUMBERS
      - ALLOW_MISSING_VALUES
      - ALLOW_TRAILING_COMMA
  - json parser features
    - Low-level I/O handling features
      - AUTO_CLOSE_SOURCE
      - ALLOW_COMMENTS
      - ALLOW_YAML_COMMENTS
      - ALLOW_UNQUOTED_FIELD_NAMES
      - ALLOW_SINGLE_QUOTES
      - ALLOW_UNQUOTED_CONTROL_CHARS
      - ALLOW_BACKSLASH_ESCAPING_ANY_CHARACTER
      - ALLOW_NUMERIC_LEADING_ZEROS
      - ALLOW_NON_NUMERIC_NUMBERS
      - ALLOW_MISSING_VALUES
      - ALLOW_TRAILING_COMMA
    - Additional input validation
      - STRICT_DUPLICATE_DETECTION
      - IGNORE_UNDEFINED
    - Misc other
      - INCLUDE_SOURCE_IN_LOCATION
  - stream write features
    - Low-level I/O handling features
      - AUTO_CLOSE_TARGET
      - AUTO_CLOSE_CONTENT
      - FLUSH_PASSED_TO_STREAM (default: true)
    - Format validation/schema features
      - IGNORE_UNKNOWN
      - STRICT_DUPLICATE_DETECTION
    - Datatype co(nv)ersions
      - WRITE_BIGDECIMAL_AS_PLAIN
    - Misc other features
      - USE_FAST_DOUBLE_WRITER
  - json write feature
    - Content escaping/quoting/encoding
      - QUOTE_FIELD_NAMES
      - WRITE_NAN_AS_STRINGS
      - WRITE_NUMBERS_AS_STRINGS
      - ESCAPE_NON_ASCII
  - json generator features
    - Low-level I/O handling features
      - AUTO_CLOSE_TARGET
      - AUTO_CLOSE_JSON_CONTENT
      - FLUSH_PASSED_TO_STREAM
    - Content escaping/quoting/encoding
      - QUOTE_FIELD_NAMES
      - QUOTE_NON_NUMERIC_NUMBERS
      - ESCAPE_NON_ASCII (default: false)
      - WRITE_NUMBERS_AS_STRINGS
      - WRITE_BIGDECIMAL_AS_PLAIN
    - Format validation/schema features
      - STRICT_DUPLICATE_DETECTION
      - IGNORE_UNKNOWN
  - databind annotations
    - Serialization (writing JSON)
      - @JsonSerialize
        - Explicit serializer
          - using
          - keyUsing
          - contentUsing
          - nullUsing
        - Explicit type
          - as
          - keyAs
          - contentAs
        - Whether static or dynamic typing
          - DYNAMIC
          - STATIC
          - DEFAULT_TYPING
        - Converter object
          - converter
          - contentConverter
    - Deserialization
      - @JsonDeserialize
        - Explicit deserializer
          - using
          - contentUsing
          - keyUsing
        - Explicit types
          - as
        - Builder object
          - builder
        - Converter object
          - converter
          - contentConverter
      - @JsonNaming
        - PropertyNamingStrategy.LowerCaseWithUnderScoresStrategy
        - PropertyNamingStrategy.PascalCaseStrategy
      - @JsonPOJOBuilder
      - @JsonValueInstantiator
    - Polymorphic type handling
      - @JsonTypeResolver
      - @JsonTypeIdResolver
  - deserialization features
    - Type conversions
      - USE_BIG_DECIMAL_FOR_FLOATS
      - USE_BIG_INTEGER_FOR_INTS
      - USE_JAVA_ARRAY_FOR_JSON_ARRAY
      - READ_ENUMS_USING_TO_STRING
    - Structural conversions
      - ACCEPT_SINGLE_VALUE_AS_ARRAY
      - UNWRAP_ROOT_VALUE
      - UNWRAP_SINGLE_VALUE_ARRAYS
    - Value conversions, coercion
      - ACCEPT_EMPTY_ARRAY_AS_NULL_OBJECT
      - ACCEPT_EMPTY_STRING_AS_NULL_OBJECT
      - ACCEPT_FLOAT_AS_INT
      - ADJUST_DATES_TO_CONTEXT_TIME_ZONE
      - READ_DATE_TIMESTAMPS_AS_NANOSECONDS
      - READ_UNKNOWN_ENUM_VALUES_AS_NULL
      - READ_UNKNOWN_ENUM_VALUES_USING_DEFAULT_VALUE
    - Failure
      - FAIL_ON_IGNORED_PROPERTIES
      - FAIL_ON_UNKNOWN_PROPERTIES
      - FAIL_ON_INVALID_SUBTYPE
      - FAIL_ON_NULL_FOR_PRIMITIVES
      - FAIL_ON_NUMBERS_FOR_ENUMS
      - FAIL_ON_READING_DUP_TREE_KEY
      - FAIL_ON_UNRESOLVED_OBJECT_IDS
      - FAIL_ON_MISSING_CREATOR_PROPERTIES
      - WRAP_EXCEPTIONS
    - Other
      - EAGER_DESERIALIZER_FETCH
  - serialization features
    - Generic output features
      - WRAP_ROOT_VALUE
        - @JsonRootName
        - @XmlRootElement
        - Simple Class name
      - INDENT_OUTPUT
    - Error handling
      - FAIL_ON_EMPTY_BEANS
      - WRAP_EXCEPTIONS
    - Output life-cycle features
      - CLOSE_CLOSEABLE
      - FLUSH_AFTER_WRITE_VALUE
    - Datatype-specific serialization
      - WRITE_DATES_AS_TIMESTAMPS
      - WRITE_DATE_KEYS_AS_TIMESTAMPS
      - WRITE_CHAR_ARRAYS_AS_JSON_ARRAYS
      - WRITE_ENUMS_USING_TO_STRING
      - WRITE_ENUMS_USING_INDEX
      - WRITE_NULL_MAP_VALUES
      - WRITE_EMPTY_JSON_ARRAYS
      - WRITE_SINGLE_ELEM_ARRAYS_UNWRAPPED
      - WRITE_BIGDECIMAL_AS_PLAIN
      - WRITE_DATE_TIMESTAMPS_AS_NANOSECONDS
      - ORDER_MAP_ENTRIES_BY_KEYS
    - Other
      - EAGER_SERIALIZER_FETCH
      - USE_EQUALITY_FOR_OBJECT_ID
  - mapper features
    - Annotation handling
      - USE_ANNOTATIONS
    - Introspection, property detection
      - AUTO_DETECT_CREATORS
      - AUTO_DETECT_FIELDS
      - AUTO_DETECT_GETTERS
      - AUTO_DETECT_IS_GETTERS
      - AUTO_DETECT_SETTERS
      - REQUIRE_SETTERS_FOR_GETTERS
      - USE_GETTERS_AS_SETTERS
      - INFER_CREATOR_FROM_CONSTRUCTOR_PROPERTIES
      - INFER_PROPERTY_MUTATORS
      - ALLOW_FINAL_FIELDS_AS_MUTATORS
      - ALLOW_VOID_VALUED_PROPERTIES
    - Reflection, access
      - CAN_OVERRIDE_ACCESS_MODIFIERS
      - OVERRIDE_PUBLIC_ACCESS_MODIFIERS
    - Name handling
      - SORT_PROPERTIES_ALPHABETICALLY
      - USE_WRAPPER_NAME_AS_PROPERTY_NAME
      - ACCEPT_CASE_INSENSITIVE_ENUMS
      - ACCEPT_CASE_INSENSITIVE_PROPERTIES
      - ACCEPT_CASE_INSENSITIVE_VALUES
      - ALLOW_EXPLICIT_PROPERTY_RENAMING
      - USE_STD_BEAN_NAMING
    - Other
      - ALLOW_COERCION_OF_SCALARS
      - DEFAULT_VIEW_INCLUSION
      - IGNORE_DUPLICATE_MODULE_REGISTRATIONS
      - IGNORE_MERGE_FOR_UNMERGEABLE
      - USE_BASE_TYPE_AS_DEFAULT_IMPL
      - USE_STATIC_TYPING
      - BLOCK_UNSAFE_POLYMORPHIC_BASE_TYPES