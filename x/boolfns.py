import abc
import functools
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang


P = ta.ParamSpec('P')


##


@dc.dataclass(frozen=True)
class BoolFn(lang.Abstract, lang.Sealed, ta.Generic[P]):
    @property
    def children(self) -> ta.Sequence['BoolFn[P]']:
        return ()

    @abc.abstractmethod
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> bool:
        raise NotImplementedError

    @classmethod
    def of(cls, fn: ta.Callable[P, bool]) -> 'BoolFn[P]':
        return of(fn)

    def __and__(self, other: ta.Callable[P, bool]) -> 'BoolFn[P]':
        return and_(self, other)

    def __rand__(self, other: ta.Callable[P, bool]) -> 'BoolFn[P]':
        return and_(other, self)

    def __or__(self, other: ta.Callable[P, bool]) -> 'BoolFn[P]':
        return or_(self, other)

    def __ror__(self, other: ta.Callable[P, bool]) -> 'BoolFn[P]':
        return or_(other, self)

    def __invert__(self) -> 'BoolFn[P]':
        return not_(self)


@dc.dataclass(frozen=True)
class FnBoolFn(BoolFn[P], lang.Final):
    fn: ta.Callable[P, bool] = dc.xfield(validate=lambda fn: callable(fn) and not isinstance(fn, BoolFn))

    def __post_init__(self) -> None:
        lang.update_wrapper(self, self.fn, setattr=object.__setattr__, exclude='__dict__')

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> bool:
        return self.fn(*args, **kwargs)


@dc.dataclass(frozen=True)
class NotBoolFn(BoolFn[P], lang.Final):
    child: BoolFn[P] = dc.xfield(check_type=BoolFn)

    @property
    def children(self) -> ta.Sequence[BoolFn[P]]:
        return (self.child,)

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> bool:
        return not self.child(*args, **kwargs)


@dc.dataclass(frozen=True)
class _CompBoolFn(BoolFn[P], lang.Abstract):  # noqa
    children: ta.Sequence[BoolFn[P]] = dc.xfield(override=True)

    def __post_init__(self) -> None:
        for c in self.children:
            check.isinstance(c, BoolFn)


@dc.dataclass(frozen=True)
class AndBoolFn(_CompBoolFn[P], lang.Final):
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> bool:
        for c in self.children:
            if not c(*args, **kwargs):
                return False
        return True


@dc.dataclass(frozen=True)
class OrBoolFn(_CompBoolFn[P], lang.Final):
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> bool:
        for c in self.children:
            if c(*args, **kwargs):
                return True
        return False


def of(fn: ta.Callable[P, bool]) -> BoolFn[P]:
    if isinstance(fn, BoolFn):
        return fn
    else:
        return FnBoolFn(fn)  # type: ignore


def _comp(cls: type[BoolFn[P]], *fns: ta.Callable[P, bool]) -> BoolFn[P]:
    if not fns:
        raise ValueError(fns)
    elif len(fns) == 1:
        return of(fns)  # type: ignore
    else:
        return cls([of(fn) for fn in fns])


and_ = functools.partial(_comp, AndBoolFn)
or_ = functools.partial(_comp, OrBoolFn)


def not_(fn: ta.Callable[P, bool]) -> BoolFn[P]:
    if isinstance(fn, NotBoolFn):
        return fn.child
    else:
        return NotBoolFn(of(fn))  # type: ignore


##


def _main() -> None:
    bfn: BoolFn[int] = of(lambda x: x < 3)
    assert bfn(2)
    assert not bfn(3)

    assert not (~bfn)(2)
    assert (~bfn)(3)

    bfn |= (lambda x: x == 5)
    assert not bfn(4)
    assert bfn(5)

    assert (~bfn)(4)
    assert not (~bfn)(5)


if __name__ == '__main__':
    _main()
