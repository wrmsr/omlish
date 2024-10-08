"""
FIXME:
 - str / list special case
 - ... pil image to b64 lol
"""
from omlish import lang
from omlish import marshal as msh

from .content import ExtendedContent


@lang.static_init
def _install_standard_marshalling() -> None:
    extended_content_poly = msh.polymorphism_from_subclasses(ExtendedContent, naming=msh.Naming.SNAKE)
    msh.STANDARD_MARSHALER_FACTORIES[0:0] = [
        msh.PolymorphismMarshalerFactory(extended_content_poly),
    ]
    msh.STANDARD_UNMARSHALER_FACTORIES[0:0] = [
        msh.PolymorphismUnmarshalerFactory(extended_content_poly),
    ]
