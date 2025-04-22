import abc
import dataclasses as dc
import typing as ta

from omlish import lang
from omlish.configs import all as cfgs


PrecheckConfigT = ta.TypeVar('PrecheckConfigT', bound='Precheck.Config')


##


@dc.dataclass(frozen=True, kw_only=True)
class PrecheckContext:
    src_roots: ta.Sequence[str]


##


class Precheck(cfgs.Configurable[PrecheckConfigT], lang.Abstract):
    @dc.dataclass(frozen=True)
    class Config(cfgs.Configurable.Config):
        pass

    @dc.dataclass(frozen=True)
    class Violation:
        pc: 'Precheck'
        msg: str

    @abc.abstractmethod
    def run(self) -> ta.AsyncIterator[Violation]:
        raise NotImplementedError
