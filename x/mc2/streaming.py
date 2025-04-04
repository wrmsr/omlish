"""
TODO:
"""
import abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .services import ResponseOutput  # noqa
from .resources import ResourcesResponse


ResponseOutputT = ta.TypeVar('ResponseOutputT', bound='ResponseOutput')

StreamResponseItemT = ta.TypeVar('StreamResponseItemT')


##


@dc.dataclass(frozen=True)
@dc.extra_params(repr_id=True)
class StreamResponse(
    ResourcesResponse[ResponseOutputT],
    lang.Abstract,
    ta.Generic[ResponseOutputT, StreamResponseItemT],
):
    @abc.abstractmethod
    def __iter__(self) -> ta.Iterator[StreamResponseItemT]:
        raise NotImplementedError
