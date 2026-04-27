from omlish import inject as inj
from omlish import lang
from omlish import lifecycles as lc

from .entrypoints.configs import EntrypointConfig


with lang.auto_proxy_import(globals()):
    from . import asyncs
    from .entrypoints import inject as _entrypoints


##


def bind_main(
        *,
        entrypoint_cfg: EntrypointConfig,
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
        _entrypoints.bind_entrypoints(
            entrypoint_cfg,
            profile_name=profile_name,
        ),
    ])

    #

    els.extend([
        inj.bind(asyncs.AsyncThreadRunner, to_ctor=asyncs.AsyncioAsyncThreadRunner),
    ])

    #

    return inj.as_elements(*els)
