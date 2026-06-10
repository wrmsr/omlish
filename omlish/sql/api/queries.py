import enum
import typing as ta

from ... import check
from ... import dataclasses as dc
from ... import lang


##


class QueryMode(enum.Enum):
    QUERY = enum.auto()
    EXEC = enum.auto()

    @classmethod
    def of(
            cls,
            o: str | QueryMode | None,
            default: QueryMode | None = None,
    ) -> QueryMode:
        if o is None:
            return check.not_none(check.isinstance(default, cls))
        elif isinstance(o, str):
            return cls[o.upper()]  # noqa
        elif isinstance(o, cls):
            return o
        else:
            raise TypeError(o)


##


@dc.dataclass(frozen=True)
class QueryParams(lang.Abstract, lang.Sealed):
    """
    Normalized, driver-agnostic bound parameters for a Query. Positional-vs-named shape follows the param style; each
    backend interprets these per its own driver call convention (execute vs executemany, spread vs not).
    """


@dc.dataclass(frozen=True)
class NoParams(QueryParams, lang.Singleton):
    pass


@dc.dataclass(frozen=True)
class RowParams(QueryParams, lang.Final):
    values: ta.Sequence[ta.Any] | ta.Mapping[str, ta.Any]


@dc.dataclass(frozen=True)
class ManyParams(QueryParams, lang.Final):
    rows: ta.Sequence[ta.Sequence[ta.Any] | ta.Mapping[str, ta.Any]]


##


class Queryable(lang.Abstract, lang.Sealed):
    pass


@ta.final
@dc.dataclass(frozen=True)
class Query(Queryable, lang.Final):
    mode: QueryMode
    text: str
    params: QueryParams = NoParams()
