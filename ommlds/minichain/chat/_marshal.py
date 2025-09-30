"""
TODO:
 - externally attach msh metadata one way or another to add omit_if_empty to Message fields
"""
from omlish import lang
from omlish import marshal as msh

from .messages import AnyAiMessage
from .messages import AnyUserMessage
from .messages import Message


##


@lang.static_init
def _install_standard_marshaling() -> None:
    for cls in [
        AnyAiMessage,
        AnyUserMessage,
        Message,
    ]:
        cls_poly = msh.polymorphism_from_subclasses(
            cls,
            naming=msh.Naming.SNAKE,
            strip_suffix='Message',
        )
        msh.install_standard_factories(
            msh.PolymorphismMarshalerFactory(cls_poly),
            msh.PolymorphismUnmarshalerFactory(cls_poly),
        )
