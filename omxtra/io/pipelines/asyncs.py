# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import dataclasses as dc
import typing as ta

from omlish.lite.namespaces import NamespaceClass

from .core import ChannelPipelineMessages


T = ta.TypeVar('T')


##


class AsyncChannelPipelineMessages(NamespaceClass):
    @ta.final
    @dc.dataclass(frozen=True)
    class Await(
        ChannelPipelineMessages.Completable[T],
        ChannelPipelineMessages.NeverInbound,
        ta.Generic[T],
    ):
        obj: ta.Awaitable[T]
