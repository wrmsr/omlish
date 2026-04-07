import abc
import typing as ta

from omlish import lang
from omlish import orm


##


class Orm(lang.Abstract):
    @abc.abstractmethod
    def new_session(self) -> ta.AsyncContextManager[orm.Session]:
        raise NotImplementedError

    @abc.abstractmethod
    def ensure_session(self) -> ta.AsyncContextManager[orm.Session]:
        raise NotImplementedError
