from ... import marshal as msh
from .dtypes import Dtype


##


def _install_poly(cfgs: msh.ConfigRegistry, cls: type) -> None:
    p = msh.polymorphism_from_subclasses(cls, naming=msh.Naming.SNAKE)
    msh.install_standard_factories(
        cfgs,
        msh.PolymorphismMarshalerFactory(p),
        msh.PolymorphismUnmarshalerFactory(p),
    )


@msh.register_global_lazy_init
def _install_standard_marshaling(cfgs: msh.ConfigRegistry) -> None:
    _install_poly(cfgs, Dtype)
