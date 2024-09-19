import abc
import dataclasses as dc
import typing as ta


PrecheckConfigT = ta.TypeVar('PrecheckConfigT', bound='Precheck.Config')


##


@dc.dataclass(frozen=True, kw_only=True)
class PrecheckContext:
    src_roots: ta.Sequence[str]


##


class Precheck(abc.ABC, ta.Generic[PrecheckConfigT]):
    @dc.dataclass(frozen=True)
    class Config:
        pass

    def __init__(self, context: PrecheckContext, config: PrecheckConfigT) -> None:
        super().__init__()
        self._context = context
        self._config = config

    @dc.dataclass(frozen=True)
    class Violation:
        pc: 'Precheck'
        msg: str

    @abc.abstractmethod
    def run(self) -> ta.AsyncIterator[Violation]:
        raise NotImplementedError
