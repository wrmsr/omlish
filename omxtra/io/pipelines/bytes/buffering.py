# ruff: noqa: UP045
# @omlish-lite
import abc
import typing as ta

from omlish.lite.abstract import Abstract

from ..core import ChannelPipelineHandler


##


class InboundBytesBufferingChannelPipelineHandler(ChannelPipelineHandler, Abstract):
    @abc.abstractmethod
    def inbound_buffered_bytes(self) -> ta.Optional[int]:
        """Returning `None` denotes currently unknown/unanswerable."""

        raise NotImplementedError


class OutboundBytesBufferingChannelPipelineHandler(ChannelPipelineHandler, Abstract):
    @abc.abstractmethod
    def outbound_buffered_bytes(self) -> ta.Optional[int]:
        """Returning `None` denotes currently unknown/unanswerable."""

        raise NotImplementedError
