# ruff: noqa: UP007 UP045
import typing as ta


##


class TextChatCompletionResponseFormat(ta.TypedDict):
    type: ta.Literal['text']


#


class JsonSchemaChatCompletionResponseFormatJsonSchema(ta.TypedDict, total=False):
    name: ta.Required[str]
    description: str
    schema: ta.Mapping[str, ta.Any]
    strict: bool


class JsonSchemaChatCompletionResponseFormat(ta.TypedDict):
    json_schema: JsonSchemaChatCompletionResponseFormatJsonSchema
    type: ta.Literal['json_schema']


#


class JsonObjectChatCompletionResponseFormat(ta.TypedDict):
    type: ta.Literal['json_object']


#


ChatCompletionResponseFormat: ta.TypeAlias = ta.Union[
    TextChatCompletionResponseFormat,
    JsonSchemaChatCompletionResponseFormat,
    JsonObjectChatCompletionResponseFormat,
]
