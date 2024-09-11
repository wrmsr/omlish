import typing as ta


T = ta.TypeVar('T')


##


class NotGiven:
    pass

NOT_GIVEN = NotGiven()


class Omit:
    pass


Headers: ta.TypeAlias = ta.Mapping[str, str | Omit]

Query: ta.TypeAlias = ta.Mapping[str, ta.Any]

Body: ta.TypeAlias = ta.Any


@ta.runtime_checkable
class Stream(ta.Protocol[T]):
    def __next__(self) -> T:
        ...

    def __iter__(self) -> ta.Iterator[T]:
        ...

    def __enter__(self) -> ta.Self:
        ...

    def __exit__(self, exc_type, exc_val, exc_tb):
        ...
