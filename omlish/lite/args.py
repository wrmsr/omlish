import dataclasses as dc
import typing as ta

from .maybes import Maybe


T = ta.TypeVar('T')


##


@dc.dataclass(init=False)
class Args:
    args: ta.Sequence[ta.Any]
    kwargs: ta.Mapping[str, ta.Any]

    def __init__(self, *args: ta.Any, **kwargs: ta.Any) -> None:
        super().__init__()

        self.args = args
        self.kwargs = kwargs

    def __bool__(self) -> bool:
        return bool(self.args) or bool(self.kwargs)

    def update(self, *args: ta.Any, **kwargs: ta.Any) -> 'Args':
        return Args(
            *self.args,
            *args,
            **{
                **self.kwargs,
                **kwargs,
            },
        )

    def map(self, fn: ta.Callable[[ta.Any], ta.Any]) -> 'Args':
        return Args(
            *[fn(a) for a in self.args],
            **{k: fn(v) for k, v in self.kwargs.items()},
        )

    def map_maybe(self, fn: ta.Callable[[ta.Any], Maybe[ta.Any]]) -> 'Args':
        return Args(
            *[n for a in self.args if (n := fn(a)).present],
            **{k: n for k, v in self.kwargs.items() if (n := fn(v)).present},
        )

    def __call__(self, fn: ta.Callable[..., T]) -> T:
        return fn(*self.args, **self.kwargs)

    @staticmethod
    def call(fn: ta.Callable[..., T], args: ta.Optional['Args']) -> T:
        if args is not None:
            return args(fn)
        else:
            return fn()

    EMPTY: ta.ClassVar['Args']


Args.EMPTY = Args()
