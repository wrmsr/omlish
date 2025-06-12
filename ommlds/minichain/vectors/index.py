import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ..registry import register_type
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


VectorIndexRequest: ta.TypeAlias = Request[VectorIndexed, VectorIndexOption]


##


class VectorIndexOutput(Output, lang.Abstract, lang.Sealed):
    pass


VectorIndexResponse: ta.TypeAlias = Response[None, VectorIndexOutput]


##


# @omlish-manifest ommlds.minichain.registry.RegistryTypeManifest
VectorIndexService: ta.TypeAlias = Service[VectorIndexRequest, VectorIndexResponse]

register_type(VectorIndexService, module=__name__)
