from omlish import lang
from omlish import marshal as msh

from .messages import Message


@lang.static_init
def _install_standard_marshalling() -> None:
    msgs_poly = msh.polymorphism_from_subclasses(Message, naming=msh.Naming.SNAKE, strip_suffix=True)
    msh.STANDARD_MARSHALER_FACTORIES[0:0] = [msh.PolymorphismMarshalerFactory(msgs_poly)]
    msh.STANDARD_UNMARSHALER_FACTORIES[0:0] = [msh.PolymorphismUnmarshalerFactory(msgs_poly)]
