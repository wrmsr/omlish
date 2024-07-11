import dataclasses as dc
import typing as ta


T = ta.TypeVar('T')


@dc.dataclass(init=False)
class Args:
    args: ta.Sequence[ta.Any]
    kwargs: ta.Mapping[str, ta.Any]

    def __init__(self, *args: ta.Any, **kwargs: ta.Any) -> None:
        super().__init__()
        self.args = args
        self.kwargs = kwargs

    def __call__(self, fn: ta.Callable[..., T]) -> T:
        return fn(*self.args, **self.kwargs)


def _main():
    def f(x, y, z):
        return x + y * z

    assert Args(1, 2, 3)(f) == 7


if __name__ == '__main__':
    _main()
