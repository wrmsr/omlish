import abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .content import Content
from .standard import StandardContent


##


@dc.dataclass(frozen=True)
class CompositeContent(StandardContent, lang.Abstract):
    @abc.abstractmethod
    def child_content(self) -> ta.Sequence[Content]:
        raise NotImplementedError

    @abc.abstractmethod
    def _replace_child_content(self, new_child_content: ta.Sequence[Content]) -> ta.Self:
        raise NotImplementedError

    def replace_child_content(self, new_child_content: ta.Sequence[Content]) -> ta.Self:
        if lang.seqs_identical(new_child_content, self.child_content()):
            return self

        return self._replace_child_content(new_child_content)
