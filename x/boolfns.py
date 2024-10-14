import abc
import dataclasses as dc
import typing as ta

from omlish import check
from omlish import lang


P = ta.ParamSpec('P')


##


@dc.dataclass(frozen=True)
class BoolFn(lang.Abstract, lang.Sealed, ta.Generic[P]):
    @abc.abstractmethod
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> bool:
        raise NotImplementedError

    @classmethod
    def of(cls, fn: ta.Callable[P, bool]) -> 'BoolFn[P]':
        if isinstance(fn, BoolFn):
            return fn
        else:
            return FnBoolFn(fn)


@dc.dataclass(frozen=True)
class FnBoolFn(BoolFn[P], lang.Final):
    fn: ta.Callable[P, bool]

    def __post_init__(self) -> None:
        check.callable(self.fn)
        check.not_isinstance(self.fn, BoolFn)
        lang.update_wrapper(self, self.fn, setattr=object.__setattr__, exclude='__dict__')

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> bool:
        return self.fn(*args, **kwargs)


##


def _main() -> None:
    bfn = BoolFn.of(lambda x: x < 3)
    assert bfn(2)
    assert not bfn(3)


if __name__ == '__main__':
    _main()
