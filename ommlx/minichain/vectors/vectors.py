import typing as ta

from omlish import dataclasses as dc


##


@dc.dataclass(frozen=True)
class Vector:
    """array.array('f' | 'd', ...) preferred"""

    v: ta.Sequence[float]
