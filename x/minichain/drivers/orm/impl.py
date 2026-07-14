import typing as ta

from omlish import lang
from omlish import orm

from .types import Orm


##


class OrmImpl(Orm):
    def __init__(
            self,
            *,
            registry: orm.Registry,
            store: orm.Store,
    ) -> None:
        super().__init__()

        self._registry = registry
        self._store = store

    def new_session(self) -> ta.AsyncContextManager[orm.Session]:
        return orm.session(self._registry, self._store)

    def ensure_session(self) -> ta.AsyncContextManager[orm.Session]:
        if (sess := orm.opt_active_session()) is not None:
            return lang.ValueAsyncContextManager(sess)
        else:
            return self.new_session()
