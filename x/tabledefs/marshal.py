from omlish import lang
from omlish import marshal as msh

from .datatypes import Datatype
from .elements import Element


def _install_poly(cls: type) -> None:
    p = msh.polymorphism_from_subclasses(cls, naming=msh.Naming.SNAKE)
    msh.STANDARD_MARSHALER_FACTORIES[0:0] = [msh.PolymorphismMarshalerFactory(p)]
    msh.STANDARD_UNMARSHALER_FACTORIES[0:0] = [msh.PolymorphismUnmarshalerFactory(p)]


@lang.cached_function
def _install_standard_marshalling() -> None:
    _install_poly(Datatype)
    _install_poly(Element)


_install_standard_marshalling()
