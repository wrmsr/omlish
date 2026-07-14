import abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .general import GeneralTransform


T = ta.TypeVar('T')


##


class SequenceTransform(lang.Abstract, ta.Generic[T]):
    @abc.abstractmethod
    def transform(self, seq: ta.Sequence[T]) -> ta.Sequence[T]:
        raise NotImplementedError


##


@dc.dataclass(frozen=True)
class CompositeSequenceTransform(SequenceTransform[T]):
    ts: ta.Sequence[SequenceTransform[T]]

    def transform(self, seq: ta.Sequence[T]) -> ta.Sequence[T]:
        for t in self.ts:
            seq = t.transform(seq)
        return seq


@dc.dataclass(frozen=True)
class FnSequenceTransform(SequenceTransform[T]):
    fn: ta.Callable[[ta.Sequence[T]], ta.Sequence[T]]

    def transform(self, seq: ta.Sequence[T]) -> ta.Sequence[T]:
        return self.fn(seq)


##


@dc.dataclass(frozen=True)
class GeneralTransformSequenceTransform(SequenceTransform[T]):
    gt: GeneralTransform[T]

    def transform(self, seq: ta.Sequence[T]) -> ta.Sequence[T]:
        return [o for i in seq for o in self.gt.transform(i)]
