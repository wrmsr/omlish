"""
TODO:
 - _stream_closer hidden kwarg? prob wanna support dc.replace
  - more generalized notion of resources? refcounted?
"""
import abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .services import Response
from .services import ResponseOutput  # noqa


ResponseOutputT = ta.TypeVar('ResponseOutputT', bound='ResponseOutput')

StreamResponseItemT = ta.TypeVar('StreamResponseItemT')


##


@dc.dataclass(frozen=True)
class StreamResponse(
    Response[ResponseOutputT],
    lang.Abstract,
    ta.Generic[ResponseOutputT, StreamResponseItemT],
):
    @abc.abstractmethod
    def __iter__(self) -> ta.Iterator[StreamResponseItemT]:
        raise NotImplementedError
