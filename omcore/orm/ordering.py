import typing as ta

from .. import check
from .. import dataclasses as dc
from .. import lang


OrderByDir: ta.TypeAlias = ta.Literal['asc', 'desc']


##


ORDER_BY_DIR_VALUES: tuple[str, ...] = ('asc', 'desc')


@ta.final
@dc.dataclass(frozen=True)
@dc.extra_class_params(terse_repr=True)
class OrderByItem(lang.Final):
    name: str
    dir: OrderByDir

    def __post_init__(self) -> None:
        check.in_(self.dir, ORDER_BY_DIR_VALUES)


Ordering: ta.TypeAlias = ta.Sequence[OrderByItem]
