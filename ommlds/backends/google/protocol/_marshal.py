from omlish import lang
from omlish import marshal as msh

from .types import Value


##


@lang.static_init
def _install_standard_marshaling() -> None:
    msh.install_standard_factories(
        *msh.standard_polymorphism_factories(
            msh.polymorphism_from_subclasses(Value),
        ),
    )
