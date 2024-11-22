import dataclasses as dc
import typing as ta


T = ta.TypeVar('T')


@dc.dataclass(frozen=True)
class Func(ta.Generic[T]):
    fn: ta.Callable[..., T]

    def __call__(self, *args: ta.Any, **kwargs: ta.Any) -> T:
        return self.fn(*args, **kwargs)
