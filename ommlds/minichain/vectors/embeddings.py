import typing as ta

from omlish import lang

from ..content.content import Content
from ..registry import register_type
from ..services import Request
from ..services import Response
from ..services import Service
from ..types import Option
from ..types import Output
from .types import Vector


##


class EmbeddingOption(Option, lang.Abstract, lang.Sealed):
    pass


EmbeddingRequest: ta.TypeAlias = Request[Content, EmbeddingOption]


##


class EmbeddingOutput(Output, lang.Abstract, lang.Sealed):
    pass


EmbeddingResponse: ta.TypeAlias = Response[Vector, EmbeddingOutput]


##


# @omlish-manifest ommlds.minichain.registry.RegistryTypeManifest
EmbeddingService: ta.TypeAlias = Service[EmbeddingRequest, EmbeddingResponse]

register_type(EmbeddingService, module=__name__)
