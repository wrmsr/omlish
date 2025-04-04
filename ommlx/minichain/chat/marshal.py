from omlish import lang
from omlish import marshal as msh

from .messages import Message


##


@lang.static_init
def _install_standard_marshalling() -> None:
    msgs_poly = msh.polymorphism_from_subclasses(Message, naming=msh.Naming.SNAKE, strip_suffix=True)
    msh.install_standard_factories(
        msh.PolymorphismMarshalerFactory(msgs_poly),
        msh.PolymorphismUnmarshalerFactory(msgs_poly),
    )
