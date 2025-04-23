import dataclasses as dc
import enum
import functools
import typing as ta

from ... import check
from ... import lang


##


class QueryMode(enum.Enum):
    QUERY = enum.auto()
    EXEC = enum.auto()

    @classmethod
    def of(
            cls,
            o: ta.Union[str, 'QueryMode', None],
            default: ta.Optional['QueryMode'] = None,
    ) -> 'QueryMode':
        if o is None:
            return check.not_none(check.isinstance(default, cls))
        elif isinstance(o, str):
            return cls[o.upper()]  # noqa
        elif isinstance(o, cls):
            return o
        else:
            raise TypeError(o)


@dc.dataclass(frozen=True)
class Query(lang.Final):
    mode: QueryMode
    text: str
    args: ta.Sequence[ta.Any]


##


@functools.singledispatch
def as_query(
        obj: ta.Any,
        *args: ta.Any,
        mode: QueryMode | str | None = None,
        **kwargs: ta.Any,
) -> Query:
    raise TypeError(obj)


@as_query.register
def _(
        q: Query,
        *,
        mode: QueryMode | str | None = None,
) -> Query:
    if mode is not None:
        check.arg(q.mode is QueryMode.of(mode))

    return q


@as_query.register
def _(
        s: str,
        *args: ta.Any,
        mode: QueryMode | str | None = None,
) -> Query:
    return Query(
        mode=QueryMode.of(mode, QueryMode.QUERY),
        text=s,
        args=args,
    )
