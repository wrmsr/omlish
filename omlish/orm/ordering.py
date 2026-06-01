# ruff: noqa: UP007
import typing as ta


OrderByDirection: ta.TypeAlias = ta.Literal['asc', 'desc']

OrderByItem: ta.TypeAlias = ta.Union[
    str,
    tuple[str, OrderByDirection],
]

Ordering: ta.TypeAlias = ta.Sequence[OrderByItem]
