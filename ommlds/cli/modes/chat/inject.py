from omlish import inject as inj
from omlish import lang

from .... import minichain as mc
from ..base import Mode
from .configs import ChatConfig


with lang.auto_proxy_import(globals()):
    from ...interfaces.bare.printing import inject as _printing
    from . import backends as _backends
    from . import mode as _mode
    from .drivers import inject as _drivers
    from .interfaces import inject as _interfaces


##


def bind_chat(cfg: ChatConfig = ChatConfig()) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.extend([
        _drivers.bind_driver(cfg.driver),

        mc.facades.inject.bind_facade(cfg.facade),

        _interfaces.bind_interface(cfg.interface),

        _printing.bind_printing(cfg.printing),
    ])

    #

    els.extend([
        # inj.bind(cfg),  # NOTE: *not* done - the code is properly structured around not needing it.
        inj.bind(Mode, to_ctor=_mode.ChatMode, singleton=True),
    ])

    #

    if (be := cfg.driver.backend.backend) is not None:
        els.append(inj.bind(_backends.InitialBackendSpec, to_const=mc.BackendSpec.of(be)))

    els.extend([
        inj.bind(_backends.BackendManager, singleton=True),
        inj.bind(
            _backends.BackendSpecGetter,
            to_fn=inj.target(bm=_backends.BackendManager)(lambda bm: bm.get_backend_spec),
            singleton=True,
        ),
    ])

    #

    return inj.as_elements(*els)
