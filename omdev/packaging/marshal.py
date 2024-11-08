from omlish import lang
from omlish import marshal as msh
from omlish import reflect as rfl

from .requires import RequiresMarkerList


##


class MarshalRequiresMarkerList(lang.NotInstantiable, lang.Final):
    pass


##


@lang.static_init
def _install_standard_marshalling() -> None:
    msh.GLOBAL_REGISTRY.register(
        RequiresMarkerList,
        msh.ReflectOverride(MarshalRequiresMarkerList),
        identity=True,
    )
