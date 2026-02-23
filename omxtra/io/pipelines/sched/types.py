# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import abc
import typing as ta

from omlish.lite.abstract import Abstract

from ..core import ChannelPipelineHandlerRef
from ..core import ChannelPipelineService


##


class ChannelPipelineScheduling(ChannelPipelineService, Abstract):
    class Handle(Abstract):
        @abc.abstractmethod
        def cancel(self) -> None:
            raise NotImplementedError

    @abc.abstractmethod
    def schedule(self, handler_ref: ChannelPipelineHandlerRef, msg: ta.Any) -> Handle:
        raise NotImplementedError

    @abc.abstractmethod
    def cancel_all(self, handler_ref: ta.Optional[ChannelPipelineHandlerRef] = None) -> None:
        raise NotImplementedError
