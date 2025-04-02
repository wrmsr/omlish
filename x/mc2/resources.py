"""
TODO:
 - _stream_closer hidden kwarg? prob wanna support dc.replace
  - more generalized notion of resources? refcounted?
"""
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .services import Response
from .services import ResponseOutput  # noqa


ResponseOutputT = ta.TypeVar('ResponseOutputT', bound='ResponseOutput')


##


class Resources:
    pass


##


@dc.dataclass(frozen=True)
class ResourcesResponse(
    Response[ResponseOutputT],
    lang.Abstract,
    ta.Generic[ResponseOutputT],
):
    _resources: Resources = dc.field(kw_only=True)
