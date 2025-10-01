from omlish import lang
from omlish import marshal as msh

from .chatcompletion.contentpart import ChatCompletionContentPart
from .chatcompletion.message import ChatCompletionMessage
from .chatcompletion.responseformat import ChatCompletionResponseFormat


##


@lang.static_init
def _install_standard_marshaling() -> None:
    for root_cls, tag_field in [
        (ChatCompletionContentPart, 'type'),
        (ChatCompletionMessage, 'role'),
        (ChatCompletionResponseFormat, 'type'),
    ]:
        msh.install_standard_factories(*msh.standard_polymorphism_factories(
            msh.polymorphism_from_subclasses(
                root_cls,
                naming=msh.Naming.SNAKE,
                strip_suffix=msh.AutoStripSuffix,
            ),
            msh.FieldTypeTagging(tag_field),
            unions='partial',
        ))
