import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .._common import _set_class_marshal_options


##


class ChatCompletionResponseFormat(lang.Abstract, lang.Sealed):
    pass


#


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class TextChatCompletionResponseFormat(ChatCompletionResponseFormat, lang.Final):
    pass


#


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class JsonSchemaChatCompletionResponseFormat(ChatCompletionResponseFormat, lang.Final):
    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options
    class JsonSchema(lang.Final):
        name: str
        description: str | None = None
        schema: ta.Mapping[str, ta.Any] | None = None
        strict: bool | None = None

    json_schema: JsonSchema


#


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class JsonObjectChatCompletionResponseFormat(ChatCompletionResponseFormat, lang.Final):
    pass
