"""
TODO:
 - ** really might wanna get typelevel+injecty with this asap..**
 - union, per dataclasses validation
 - dumb coercers
  - verdict: presto-guice-jackson-style Encoders/Decoders + injectable registries w global dumb default
 - combo Serde - codecify?
  - dedupe symmetric generic Serde sides?
 - heavy overlap w dc validation - omnibus/validate?
  - typelevel (ta.Range[ta.Literal[0], ta.Literal[10]]) vs non..
 - camel/snake(/kebab/pascal/dot)
 - enums
 - shared object ast
  - coments, block comments, Mark, spaces, ...
  - large overlap between codegen and object serde - marks, mark chain, blanks, quoting, coments, etc
  - pandoc?
 - xml (maven gen)

builtins:
    Decimal
    dsn.DSN
    email.Email
    ipaddress.IPv4Address
    ipaddress.IPv6Address
    path.DirectoryPath
    path.FilePath
    path.PathType
    pathlib.Path
    re.Pattern
    secret.SecretBytes
    secret.SecretStr
    timedelta
    url.AbsoluteURL
    url.HostName
    url.NetworkAddress
    url.RelativeURL
    url.URL
    uuid.UUID

typical
https://github.com/marshmallow-code/marshmallow/wiki/Ecosystem
https://github.com/lidatong/dataclasses-json
https://github.com/lyft/toasted-marshmallow/blob/master/toastedmarshmallow/jit.py

https://github.com/ijl/orjson

https://serde.rs/data-model.html
https://serde.rs/examples.html

https://github.com/FasterXML/jackson-databind/wiki/Deserialization-Features
https://github.com/FasterXML/jackson-databind/wiki/Serialization-features
https://github.com/FasterXML/jackson-databind/wiki/Databind-annotations
https://github.com/FasterXML/jackson-databind/wiki/Mapper-Features

subtype reg:
@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, include = JsonTypeInfo.As.PROPERTY, property = "@type")
@JsonSubTypes({@JsonSubTypes.Type(value = OutputNode.class, name = "output"), ...

objectMapper.disable(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES);
objectMapper.disable(DeserializationFeature.ACCEPT_FLOAT_AS_INT);
objectMapper.disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS);
objectMapper.setDefaultPropertyInclusion(
    JsonInclude.Value.construct(JsonInclude.Include.NON_ABSENT, JsonInclude.Include.ALWAYS));
objectMapper.disable(MapperFeature.AUTO_DETECT_CREATORS);
objectMapper.disable(MapperFeature.AUTO_DETECT_FIELDS);
objectMapper.disable(MapperFeature.AUTO_DETECT_SETTERS);
objectMapper.disable(MapperFeature.AUTO_DETECT_GETTERS);
objectMapper.disable(MapperFeature.AUTO_DETECT_IS_GETTERS);
objectMapper.disable(MapperFeature.USE_GETTERS_AS_SETTERS);
objectMapper.disable(MapperFeature.CAN_OVERRIDE_ACCESS_MODIFIERS);
objectMapper.disable(MapperFeature.INFER_PROPERTY_MUTATORS);
objectMapper.disable(MapperFeature.ALLOW_FINAL_FIELDS_AS_MUTATORS);

public static final Set<MapperFeature> DEFAULT_DISABLED_FEATURES = ImmutableSet.copyOf(new MapperFeature[] {
        MapperFeature.ALLOW_FINAL_FIELDS_AS_MUTATORS,
        MapperFeature.AUTO_DETECT_CREATORS,
        MapperFeature.AUTO_DETECT_FIELDS,
        MapperFeature.AUTO_DETECT_GETTERS,
        MapperFeature.AUTO_DETECT_IS_GETTERS,
        MapperFeature.AUTO_DETECT_SETTERS,
        MapperFeature.INFER_CREATOR_FROM_CONSTRUCTOR_PROPERTIES,
        MapperFeature.INFER_PROPERTY_MUTATORS,
        MapperFeature.USE_BASE_TYPE_AS_DEFAULT_IMPL,
        MapperFeature.USE_GETTERS_AS_SETTERS,
});

public static final List<Supplier<Module>> DEFAULT_MODULE_FACTORIES = new CopyOnWriteArrayList<>(ImmutableList.of(
        GuavaModule::new,
        JavaTimeModule::new,
        Jdk8Module::new
));

public static ObjectMapper configureObjectMapper(ObjectMapper objectMapper)
{
    objectMapper.disable(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES);
    objectMapper.disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS);
    objectMapper.setSerializationInclusion(JsonInclude.Include.NON_NULL);
    DEFAULT_DISABLED_FEATURES.forEach(objectMapper::disable);
    DEFAULT_MODULE_FACTORIES.forEach(f -> objectMapper.registerModule(f.get()));
    getAfterburnerModuleFactory().ifPresent(f -> objectMapper.registerModule(f.get()));
    return objectMapper;
}

public static final Set<JsonParser.Feature> RELAXED_JSON_PARSER_ENABLED_FEATURES = ImmutableSet.of(
        JsonParser.Feature.ALLOW_COMMENTS,
        JsonParser.Feature.ALLOW_YAML_COMMENTS,
        JsonParser.Feature.ALLOW_UNQUOTED_FIELD_NAMES,
        JsonParser.Feature.ALLOW_SINGLE_QUOTES
);
"""
