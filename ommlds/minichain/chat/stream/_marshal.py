from omlish import lang
from omlish import marshal as msh

from .types import AiDelta


##


@lang.static_init
def _install_standard_marshaling() -> None:
    ad_poly = msh.polymorphism_from_subclasses(AiDelta, naming=msh.Naming.SNAKE)
    msh.install_standard_factories(
        msh.PolymorphismMarshalerFactory(ad_poly),
        msh.PolymorphismUnmarshalerFactory(ad_poly),
    )
