import abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .standard import StandardContent
from .content import Content


##


@dc.dataclass(frozen=True)
class CompositeContent(StandardContent, lang.Abstract):
    @abc.abstractmethod
    def child_content(self) -> ta.Sequence[Content]:
        raise NotImplementedError
