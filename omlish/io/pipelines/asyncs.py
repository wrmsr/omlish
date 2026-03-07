# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import dataclasses as dc
import typing as ta

from ...lite.namespaces import NamespaceClass
from .core import IoPipelineMessages


T = ta.TypeVar('T')


##


class AsyncIoPipelineMessages(NamespaceClass):
    @ta.final
    @dc.dataclass(frozen=True)
    class Await(
        IoPipelineMessages.Completable[T],
        IoPipelineMessages.NeverInbound,
        ta.Generic[T],
    ):
        obj: ta.Awaitable[T]
