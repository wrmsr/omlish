import abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang
from omlish.configs import all as cfgs


SessionConfigT = ta.TypeVar('SessionConfigT', bound='Session.Config')


##


class Session(cfgs.Configurable[SessionConfigT], lang.Abstract):
    @dc.dataclass(frozen=True)
    class Config(cfgs.Configurable.Config):
        pass

    @abc.abstractmethod
    def run(self) -> ta.Awaitable[None]:
        raise NotImplementedError
