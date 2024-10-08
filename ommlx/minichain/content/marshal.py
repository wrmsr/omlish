from omlish import lang
from omlish import marshal as msh

from .content import Content


@lang.static_init
def _install_standard_marshalling() -> None:
    content_poly = msh.polymorphism_from_subclasses(Content, naming=msh.Naming.SNAKE)
    msh.STANDARD_MARSHALER_FACTORIES[0:0] = [msh.PolymorphismMarshalerFactory(content_poly)]
    msh.STANDARD_UNMARSHALER_FACTORIES[0:0] = [msh.PolymorphismUnmarshalerFactory(content_poly)]
