from omlish import lang
from omlish import marshal as msh

from .types import AiChoiceDelta


##


@lang.static_init
def _install_standard_marshaling() -> None:
    acd_poly = msh.polymorphism_from_subclasses(AiChoiceDelta, naming=msh.Naming.SNAKE)
    msh.install_standard_factories(
        msh.PolymorphismMarshalerFactory(acd_poly),
        msh.PolymorphismUnmarshalerFactory(acd_poly),
    )
