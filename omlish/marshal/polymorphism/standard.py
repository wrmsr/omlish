import typing as ta

from ..base.types import MarshalerFactory
from ..base.types import UnmarshalerFactory
from .marshal import PolymorphismMarshalerFactory
from .metadata import Polymorphism
from .metadata import TypeTagging
from .metadata import WrapperTypeTagging
from .unions import PolymorphismUnionMarshalerFactory
from .unions import PolymorphismUnionUnmarshalerFactory
from .unmarshal import PolymorphismUnmarshalerFactory


##


def standard_polymorphism_factories(
        poly: Polymorphism,
        tt: TypeTagging = WrapperTypeTagging(),
        *,
        unions: bool | ta.Literal['partial'] = False,
) -> ta.Sequence[MarshalerFactory | UnmarshalerFactory]:
    out: list[MarshalerFactory | UnmarshalerFactory] = [
        PolymorphismMarshalerFactory(poly, tt),
        PolymorphismUnmarshalerFactory(poly, tt),
    ]

    if unions:
        out.extend([
            PolymorphismUnionMarshalerFactory(poly.impls, tt, allow_partial=unions == 'partial'),
            PolymorphismUnionUnmarshalerFactory(poly.impls, tt, allow_partial=unions == 'partial'),
        ])

    return out
