from omlish import lang
from omlish import marshal as msh

from .types import Content


##


@lang.static_init
def _install_standard_marshaling() -> None:
    for root_cls in [
        Content,
        Content.CacheControl,
    ]:
        msh.install_standard_factories(*msh.standard_polymorphism_factories(
            msh.polymorphism_from_subclasses(
                root_cls,
                naming=msh.Naming.SNAKE,
                strip_suffix=msh.AutoStripSuffix,
            ),
            msh.FieldTypeTagging('type'),
        ))
