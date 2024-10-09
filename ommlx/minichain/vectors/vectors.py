import typing as ta

from omlish import dataclasses as dc
from omlish import lang


if ta.TYPE_CHECKING:
    import numpy as np
else:
    np = lang.proxy_import('numpy')


##


Vectorable: ta.TypeAlias = 'np.ndarray'


@dc.dataclass(frozen=True)
class Vector:
    """array.array('f' | 'd', ...) preferred"""

    v: ta.Sequence[float]
