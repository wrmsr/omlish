import dataclasses as dc
import enum
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
