import typing as ta

from omlish import lang

from ..content.types import Content
from ..registries.globals import register_type
from ..services import Request
from ..services import Response
from ..services import Service
from ..types import Option
from ..types import Output
from .types import Vector


##


class EmbeddingOption(Option, lang.Abstract, lang.Sealed):
    pass


EmbeddingOptions: ta.TypeAlias = EmbeddingOption


##


class EmbeddingOutput(Output, lang.Abstract, lang.Sealed):
    pass


EmbeddingOutputs: ta.TypeAlias = EmbeddingOutput


##


EmbeddingRequest: ta.TypeAlias = Request[Content, EmbeddingOptions]

EmbeddingResponse: ta.TypeAlias = Response[Vector, EmbeddingOutputs]

# @omlish-manifest $.minichain.registries.manifests.RegistryTypeManifest
EmbeddingService: ta.TypeAlias = Service[EmbeddingRequest, EmbeddingResponse]

register_type(EmbeddingService, module=__name__)


def static_check_is_embedding_service[T: EmbeddingService](t: type[T]) -> type[T]:
    return t
