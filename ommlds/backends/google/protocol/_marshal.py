from omlish import marshal as msh

from .types import Value


##


@msh.register_global_lazy_init
def _install_standard_marshaling(cfgs: msh.ConfigRegistry) -> None:
    msh.install_standard_factories(
        cfgs,
        *msh.standard_polymorphism_factories(
            msh.polymorphism_from_subclasses(Value),
        ),
    )
