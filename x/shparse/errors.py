import abc

from omlish import dataclasses as dc
from omlish import lang


##


class Error(lang.Abstract):
    @property
    @abc.abstractmethod
    def message(self) -> str:
        raise NotImplementedError


@dc.dataclass()
class GenericError(Error):
    s: str

    @property
    def message(self) -> str:
        return self.s
