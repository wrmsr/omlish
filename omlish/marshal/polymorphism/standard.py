import typing as ta

from ..base.types import MarshalerFactory
from ..base.types import UnmarshalerFactory
from .marshal import PolymorphismMarshalerFactory
from .metadata import Polymorphism
from .metadata import TypeTagging
from .metadata import WrapperTypeTagging
from .unmarshal import PolymorphismUnmarshalerFactory


##


def standard_polymorphism_factories(
        poly: Polymorphism,
        tt: TypeTagging = WrapperTypeTagging(),
) -> ta.Sequence[MarshalerFactory | UnmarshalerFactory]:
    return [
        PolymorphismMarshalerFactory(poly, tt),
        PolymorphismUnmarshalerFactory(poly, tt),
    ]
