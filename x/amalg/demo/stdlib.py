import typing as ta


T = ta.TypeVar('T')


def check_not_none(obj: ta.Optional[T]) -> T:
    if obj is None:
        raise Exception('Must not be None')
    return obj
