"""
TODO:
 - externally attach msh metadata one way or another to add omit_if_empty to Message fields
"""
import typing as ta

from omlish import lang
from omlish import marshal as msh

from .formats import ResponseFormat  # noqa
from .messages import AnyAiMessage
from .messages import AnyUserMessage
from .messages import Message
from .metadata import MessageMetadata
from .tools.types import Tool  # noqa
from .transform.metadata import TransformedMessageOrigin  # noqa
from .types import ChatOption


##


@lang.static_init
def _install_standard_marshaling() -> None:
    cls: ta.Any

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

    for cls in [
        ChatOption,
        MessageMetadata,
    ]:
        msh.install_standard_factories(*msh.standard_polymorphism_factories(
            msh.polymorphism_from_subclasses(
                cls,
                naming=msh.Naming.SNAKE,
            ),
            msh.WrapperTypeTagging(),
        ))
