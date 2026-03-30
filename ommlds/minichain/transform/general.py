import abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang


T = ta.TypeVar('T')


##


class GeneralTransform(lang.Abstract, ta.Generic[T]):
    @abc.abstractmethod
    def transform(self, o: T) -> ta.Sequence[T]:
        raise NotImplementedError


##


@dc.dataclass(frozen=True)
class CompositeGeneralTransform(GeneralTransform[T]):
    ts: ta.Sequence[GeneralTransform[T]]

    def transform(self, o: T) -> ta.Sequence[T]:
        out: list[T] = [o]
        for mt in self.ts:
            out = [o for i in out for o in mt.transform(i)]
        return out


@dc.dataclass(frozen=True)
class FnGeneralTransform(GeneralTransform[T]):
    fn: ta.Callable[[T], ta.Sequence[T]]

    def transform(self, o: T) -> ta.Sequence[T]:
        return self.fn(o)


@dc.dataclass(frozen=True)
class TypeFilteredGeneralTransform(GeneralTransform[T]):
    ty: type | tuple[type, ...]
    t: GeneralTransform

    def transform(self, o: T) -> ta.Sequence[T]:
        if isinstance(o, self.ty):
            return self.t.transform(o)
        else:
            return [o]
