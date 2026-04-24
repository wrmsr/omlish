from omlish import inject as inj

from ..... import minichain as mc
from ..configs import ChatConfig
from .commands import BackendCommand
from .manager import BackendManager
from .types import BackendSpecGetter
from .types import InitialBackendSpec


##


def bind_backend(cfg: ChatConfig = ChatConfig()) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    if (be := cfg.driver.backend.backend) is not None:
        els.append(inj.bind(InitialBackendSpec, to_const=mc.BackendSpec.of(be)))

    els.extend([
        inj.bind(BackendManager, singleton=True),
        inj.bind(
            BackendSpecGetter,
            to_fn=inj.target(bm=BackendManager)(lambda bm: bm.get_backend_spec),
            singleton=True,
        ),
    ])

    #

    els.extend([
        inj.bind(BackendCommand, singleton=True),
        mc.facades.injection.commands().bind_item(to_key=BackendCommand),
    ])

    #

    return inj.as_elements(*els)
