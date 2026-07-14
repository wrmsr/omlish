import typing as ta

from ..api.types import MarshalerFactory
from ..api.types import UnmarshalerFactory
from .api import Polymorphism
from .api import TypeTagging
from .api import WrapperTypeTagging
from .marshal import PolymorphismMarshalerFactory
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
