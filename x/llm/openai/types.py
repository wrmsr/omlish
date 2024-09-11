import typing as ta


##


class NotGiven:
    pass

NOT_GIVEN = NotGiven()


class Omit:
    pass


Headers: ta.TypeAlias = ta.Mapping[str, str | Omit]

Query: ta.TypeAlias = ta.Mapping[str, ta.Any]

Body: ta.TypeAlias = ta.Any
