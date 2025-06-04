import typing as ta

from omlish import lang

from ..content.content import Content
from ..registry import register_type
from ..services import Request
from ..services import RequestOption
from ..services import Response
from ..services import ResponseOutput
from ..services import Service
from .types import Vector


##


class EmbeddingRequestOption(RequestOption, lang.Abstract, lang.Sealed):
    pass


EmbeddingRequest: ta.TypeAlias = Request[Content, EmbeddingRequestOption]


##


class EmbeddingResponseOutput(ResponseOutput, lang.Abstract, lang.Sealed):
    pass


EmbeddingResponse: ta.TypeAlias = Response[Vector, EmbeddingResponseOutput]


##


# @omlish-manifest ommlds.minichain.registry.RegistryTypeManifest
EmbeddingService: ta.TypeAlias = Service[EmbeddingRequest, EmbeddingResponse]

register_type(EmbeddingService, module=__name__)
