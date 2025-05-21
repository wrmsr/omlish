# FIXME: Tokens serde as scalar 'l'
from omlish import lang
from omlish import marshal as msh


##


@lang.static_init
def _install_standard_marshalling() -> None:
    msh.install_standard_factories()
