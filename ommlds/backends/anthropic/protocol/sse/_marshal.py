from omlish import lang
from omlish import marshal as msh

from .events import AnthropicSseDecoderEvents


##


@lang.static_init
def _install_standard_marshaling() -> None:
    for root_cls in [
        AnthropicSseDecoderEvents.Event,
        AnthropicSseDecoderEvents.ContentBlockStart.ContentBlock,
        AnthropicSseDecoderEvents.ContentBlockDelta.Delta,
    ]:
        msh.install_standard_factories(*msh.standard_polymorphism_factories(
            msh.polymorphism_from_subclasses(
                root_cls,
                naming=msh.Naming.SNAKE,
            ),
            msh.FieldTypeTagging('type'),
        ))
