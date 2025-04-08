import typing as ta


##


CoerceFn: ta.TypeAlias = ta.Callable[[ta.Any], ta.Any]
ValidateFn: ta.TypeAlias = ta.Callable[[ta.Any], bool]
ReprFn: ta.TypeAlias = ta.Callable[[ta.Any], str | None]

InitFn: ta.TypeAlias = ta.Callable[[ta.Any], None]
ClassValidateFn: ta.TypeAlias = ta.Callable[..., bool]


class DefaultFactory(ta.NamedTuple):
    fn: ta.Callable[..., ta.Any]
