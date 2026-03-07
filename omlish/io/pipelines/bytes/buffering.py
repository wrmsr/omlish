# ruff: noqa: UP045
# @omlish-lite
import abc
import typing as ta

from ....lite.abstract import Abstract
from ..core import IoPipelineHandler


##


class InboundBytesBufferingIoPipelineHandler(IoPipelineHandler, Abstract):
    @abc.abstractmethod
    def inbound_buffered_bytes(self) -> ta.Optional[int]:
        """Returning `None` denotes currently unknown/unanswerable."""

        raise NotImplementedError


class OutboundBytesBufferingIoPipelineHandler(IoPipelineHandler, Abstract):
    @abc.abstractmethod
    def outbound_buffered_bytes(self) -> ta.Optional[int]:
        """Returning `None` denotes currently unknown/unanswerable."""

        raise NotImplementedError
