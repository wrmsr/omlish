import dataclasses as dc
import enum
import typing as ta

from ... import check
from ... import lang


##


class QueryMode(enum.Enum):
    QUERY = enum.auto()
    EXEC = enum.auto()


@dc.dataclass(frozen=True)
class Query(lang.Final):
    mode: QueryMode
    text: str
    args: ta.Sequence[ta.Any]

    #

    @classmethod
    @ta.overload
    def of(
            cls,
            query: 'Query',
    ) -> 'Query':
        ...

    @classmethod
    @ta.overload
    def of(
            cls,
            text: str,
            *args: ta.Any,
            mode: str | QueryMode = QueryMode.QUERY,
    ) -> 'Query':
        ...

    @classmethod  # type: ignore[misc]
    def of(cls, obj, *args, **kwargs):
        if isinstance(obj, Query):
            check.arg(not args)
            check.arg(not kwargs)
            return obj

        elif isinstance(obj, str):
            mode = kwargs.pop('mode', QueryMode.QUERY)
            if isinstance(mode, str):
                mode = QueryMode[mode.upper()]
            check.arg(not kwargs)

            return cls(
                mode=mode,
                text=obj,
                args=args,
            )

        else:
            raise TypeError(obj)
