from .. import lang
from .. import marshal as msh
from .base import Bootstrap
from .harness import BOOTSTRAP_TYPES_BY_NAME


@lang.static_init
def _install_standard_marshalling() -> None:
    cfgs_poly = msh.Polymorphism(
        Bootstrap.Config,
        [msh.Impl(b.Config, n) for n, b in BOOTSTRAP_TYPES_BY_NAME.items()],
    )
    msh.install_standard_factories(
        msh.PolymorphismMarshalerFactory(cfgs_poly),
        msh.PolymorphismUnmarshalerFactory(cfgs_poly),
    )
