from omcore import marshal as msh

from .events import AnthropicSseDecoderEvents


##


@msh.register_global_lazy_init
def _install_standard_marshaling(cfgs: msh.ConfigRegistry) -> None:
    for root_cls in [
        AnthropicSseDecoderEvents.Event,
        AnthropicSseDecoderEvents.ContentBlockStart.ContentBlock,
        AnthropicSseDecoderEvents.ContentBlockDelta.Delta,
    ]:
        msh.install_standard_factories(
            cfgs,
            *msh.standard_polymorphism_factories(
                msh.polymorphism_from_subclasses(
                    root_cls,
                    naming=msh.Naming.SNAKE,
                ),
                msh.FieldTypeTagging('type'),
            ),
        )
