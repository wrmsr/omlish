from omlish import lang
from omlish import marshal as msh

from .chat import Message
from .content import Content


@lang.cached_function
def _install_standard_marshalling() -> None:
    msgs_poly = msh.polymorphism_from_subclasses(Message, naming=msh.Naming.SNAKE, strip_suffix=True)
    msh.STANDARD_MARSHALER_FACTORIES[0:0] = [msh.PolymorphismMarshalerFactory(msgs_poly)]
    msh.STANDARD_UNMARSHALER_FACTORIES[0:0] = [msh.PolymorphismUnmarshalerFactory(msgs_poly)]

    content_poly = msh.polymorphism_from_subclasses(Content, naming=msh.Naming.SNAKE)
    msh.STANDARD_MARSHALER_FACTORIES[0:0] = [msh.PolymorphismMarshalerFactory(content_poly)]
    msh.STANDARD_UNMARSHALER_FACTORIES[0:0] = [msh.PolymorphismUnmarshalerFactory(content_poly)]


_install_standard_marshalling()
