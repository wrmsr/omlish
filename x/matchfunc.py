import dataclasses as dc
import typing as ta


T = ta.TypeVar('T')
P = ta.ParamSpec('P')


class MatchGuardError(Exception):
    pass


@dc.dataclass(frozen=True)
class MatchFunc(ta.Generic[P, T]):
    guard: ta.Callable[P, bool]
    func: ta.Callable[P, T]

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        if not self.guard(*args, **kwargs):
            raise MatchGuardError
        return self.func(*args, **kwargs)


@dc.dataclass(frozen=True)
class MultiMatchFunc(ta.Generic[P, T]):
    children: ta.Sequence[MatchFunc[P, T]]

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        for c in self.children:
            if c.guard(*args, **kwargs):
                return c.func(*args, **kwargs)
        raise MatchGuardError
