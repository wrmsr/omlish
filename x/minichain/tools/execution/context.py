import typing as ta

from omcore import dataclasses as dc
from omcore import lang


T = ta.TypeVar('T')


##


@ta.final
@dc.dataclass(frozen=True)
class ToolContextProvider(lang.Final, ta.Generic[T]):
    ty: type[T]
    fn: ta.Callable[[], T]


ToolContextProviders = ta.NewType('ToolContextProviders', ta.Sequence[ToolContextProvider])
