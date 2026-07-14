import typing as ta


T = ta.TypeVar('T')


##


def all_same(l: ta.Sequence[T], r: ta.Sequence[T]) -> bool:
    return len(l) == len(r) and all(x is y for x, y in zip(l, r, strict=True))
