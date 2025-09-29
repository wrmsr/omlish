from ... import lang
from ... import marshal as msh
from .dtypes import Dtype
from .elements import Element


##


def _install_poly(cls: type) -> None:
    p = msh.polymorphism_from_subclasses(cls, naming=msh.Naming.SNAKE)
    msh.install_standard_factories(
        msh.PolymorphismMarshalerFactory(p),
        msh.PolymorphismUnmarshalerFactory(p),
    )


@lang.static_init
def _install_standard_marshaling() -> None:
    _install_poly(Dtype)
    _install_poly(Element)
