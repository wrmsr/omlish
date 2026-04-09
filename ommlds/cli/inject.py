from omlish import inject as inj
from omlish import lang
from omlish import lifecycles as lc

from .modes.configs import ModeConfig


with lang.auto_proxy_import(globals()):
    from . import asyncs
    from .modes import inject as _modes


##


def bind_main(
        *,
        mode_cfg: ModeConfig,
        profile_name: str | None = None,
) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.extend([
        lc.bind_async_lifecycle_registrar(),
        lc.bind_async_managed_lifecycle_manager(eager=True),
    ])

    #

    els.extend([
        _modes.bind_modes(
            mode_cfg,
            profile_name=profile_name,
        ),
    ])

    #

    els.extend([
        inj.bind(asyncs.AsyncThreadRunner, to_ctor=asyncs.AsyncioAsyncThreadRunner),
    ])

    #

    return inj.as_elements(*els)
