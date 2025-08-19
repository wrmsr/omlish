import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ..registries.globals import register_type
from ..services import Request
from ..services import Response
from ..services import Service
from ..types import Option
from ..types import Output
from .types import Vector


##


@dc.dataclass(frozen=True)
class VectorIndexed(lang.Final):
    v: ta.Any
    vec: Vector


##


class VectorIndexOption(Option, lang.Abstract, lang.Sealed):
    pass


VectorIndexOptions: ta.TypeAlias = VectorIndexOption


##


class VectorIndexOutput(Output, lang.Abstract, lang.Sealed):
    pass


VectorIndexOutputs: ta.TypeAlias = VectorIndexOutput


##


VectorIndexRequest: ta.TypeAlias = Request[VectorIndexed, VectorIndexOptions]

VectorIndexResponse: ta.TypeAlias = Response[None, VectorIndexOutputs]

# @omlish-manifest $.minichain.registries.manifests.RegistryTypeManifest
VectorIndexService: ta.TypeAlias = Service[VectorIndexRequest, VectorIndexResponse]

register_type(VectorIndexService, module=__name__)


def static_check_is_vector_index_service[T: VectorIndexService](t: type[T]) -> type[T]:
    return t
