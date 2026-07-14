import abc
import typing as ta

from ... import lang
from ..api.queriers import AsyncQuerier
from ..tabledefs.tabledefs import TableDef
from .reflected import ReflectedTable


##


class Inspector(lang.Abstract):
    """
    A backend's live-db introspection facet. `reflect_table` does IO - it reads the catalog via an `AsyncQuerier` - and
    is fail-open; `lift_table` is a pure, lossy conversion of the reflected snapshot into a tabledef that can be diffed
    against the in-code definition.

    Inspection is async-only (there is no sync twin): a sync caller wraps its db/conn in a `SyncToAsyncDb` /
    `SyncToAsyncConn` and drives `reflect_table` through `lang.sync_await` - which needs no event loop because a
    sync-backed querier never actually suspends.
    """

    @abc.abstractmethod
    def reflect_table(self, querier: AsyncQuerier, name: str) -> ta.Awaitable[ReflectedTable | None]:
        raise NotImplementedError

    @abc.abstractmethod
    def lift_table(self, reflected: ReflectedTable) -> TableDef:
        raise NotImplementedError
