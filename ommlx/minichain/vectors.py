import dataclasses as dc
import typing as ta


@dc.dataclass(frozen=True)
class Vector:
    """array.array('f' | 'd', ...) preferred"""

    v: ta.Sequence[float]
