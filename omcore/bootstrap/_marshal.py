from .. import marshal as msh
from .base import Bootstrap
from .harness import BOOTSTRAP_TYPES_BY_NAME


##


@msh.register_global_lazy_init
def _install_standard_marshaling(cfgs: msh.ConfigRegistry) -> None:
    cfgs_poly = msh.Polymorphism(
        Bootstrap.Config,
        [msh.Impl(b.Config, n) for n, b in BOOTSTRAP_TYPES_BY_NAME.items()],
    )
    msh.install_standard_factories(
        cfgs,
        msh.PolymorphismMarshalerFactory(cfgs_poly),
        msh.PolymorphismUnmarshalerFactory(cfgs_poly),
    )
