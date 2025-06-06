# ruff: noqa: UP007
import typing as ta


##


class TextChatCompletionResponseFormat(ta.TypedDict):
    type: ta.Literal['text']


#


class JsonSchemaResponseFormatJsonSchema(ta.TypedDict, total=False):
    name: ta.Required[str]
    description: str
    schema: ta.Mapping[str, object]
    strict: bool


class JsonSchemaResponseFormat(ta.TypedDict):
    json_schema: JsonSchemaResponseFormatJsonSchema
    type: ta.Literal['json_schema']


#


class JsonObjectResponseFormat(ta.TypedDict):
    type: ta.Literal['json_object']


#


ChatCompletionResponseFormat: ta.TypeAlias = ta.Union[
    TextChatCompletionResponseFormat,
    JsonSchemaResponseFormat,
    JsonObjectResponseFormat,
]
