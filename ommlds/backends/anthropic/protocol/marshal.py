from omlish import lang
from omlish import marshal as msh

from .sse import AnthropicSseDecoderEvents


##


@lang.static_init
def _install_standard_anthropic_sse_marshalling() -> None:
    for root_cls in [
        AnthropicSseDecoderEvents.Event,
        AnthropicSseDecoderEvents.ContentBlockStart.ContentBlock,
        AnthropicSseDecoderEvents.ContentBlockDelta.Delta,
    ]:
        poly = msh.polymorphism_from_subclasses(root_cls, naming=msh.Naming.SNAKE)
        msh.install_standard_factories(
            msh.PolymorphismMarshalerFactory(poly, msh.FieldTypeTagging('type')),
            msh.PolymorphismUnmarshalerFactory(poly, msh.FieldTypeTagging('type')),
        )
