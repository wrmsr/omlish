import typing as ta


##


InitFn: ta.TypeAlias = ta.Callable[[ta.Any], None]
ValidateFn: ta.TypeAlias = ta.Callable[..., bool]
ReprFn: ta.TypeAlias = ta.Callable[[ta.Any], str | None]


class DefaultFactory(ta.NamedTuple):
    fn: ta.Callable[..., ta.Any]
