import typing as ta

from ..base.types import MarshalerFactory
from ..base.types import UnmarshalerFactory
from .marshal import PolymorphismMarshalerFactory
from .types import Polymorphism
from .types import TypeTagging
from .types import WrapperTypeTagging
from .unmarshal import PolymorphismUnmarshalerFactory


##


def standard_polymorphism_factories(
        poly: Polymorphism,
        tt: TypeTagging = WrapperTypeTagging(),
) -> ta.Sequence[MarshalerFactory | UnmarshalerFactory]:
    out: list[MarshalerFactory | UnmarshalerFactory] = [
        PolymorphismMarshalerFactory(poly, tt),
        PolymorphismUnmarshalerFactory(poly, tt),
    ]

    return out
