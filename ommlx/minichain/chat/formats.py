from omlish import dataclasses as dc
from omlish import lang
from omlish import typedvalues as tv

from ..json import JsonSchema
from .types import ChatRequestOption


##


class ResponseFormat(ChatRequestOption, tv.UniqueTypedValue, lang.Abstract, lang.Sealed):
    pass


@dc.dataclass(frozen=True)
class TextResponseFormat(ResponseFormat, lang.Final):
    pass


TEXT_RESPONSE_FORMAT = TextResponseFormat()


@dc.dataclass(frozen=True)
class JsonResponseFormat(ResponseFormat, lang.Final):
    schema: JsonSchema | None = None


JSON_RESPONSE_FORMAT = JsonResponseFormat()
