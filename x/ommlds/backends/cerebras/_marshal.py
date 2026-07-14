from omlish import marshal as msh

from .protocol import ChatCompletionRequest


##


@msh.register_global_lazy_init
def _install_standard_marshaling(cfgs: msh.ConfigRegistry) -> None:
    for root_cls, tag_field in [
        (ChatCompletionRequest.Message, 'role'),
        (ChatCompletionRequest.ResponseFormat, 'type'),
    ]:
        msh.install_standard_factories(
            cfgs,
            *msh.standard_polymorphism_factories(
                msh.polymorphism_from_subclasses(
                    root_cls,
                    naming=msh.Naming.SNAKE,
                    strip_suffix=msh.AUTO_STRIP_SUFFIX,
                ),
                msh.FieldTypeTagging(tag_field),
            ),
        )
