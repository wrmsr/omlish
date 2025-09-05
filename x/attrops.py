# @omlish-lite
import typing as ta


T = ta.TypeVar('T')


##


class AttrOps(ta.Generic[T]):
    @ta.overload
    def __init__(self, attrs_fn: ta.Callable[[T], ta.Tuple[ta.Union[ta.Any, ta.Tuple[str, ta.Any]], ...]], /) -> None:
        ...

    @ta.overload
    def __init__(self, attrs: ta.Sequence[ta.Union[str, ta.Tuple[str, str]]], /) -> None:
        ...

    def __init__(self, arg) -> None:
        pass


##


def _main() -> None:
    pass


if __name__ == '__main__':
    _main()
