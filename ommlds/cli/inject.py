from omlish import inject as inj
from omlish import lang
from omlish import lifecycles as lc

from .sessions.configs import SessionConfig


with lang.auto_proxy_import(globals()):
    from . import asyncs
    from .sessions import inject as _sessions
    from .state import inject as _state


##


def bind_main(
        *,
        session_cfg: SessionConfig,
) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.extend([
        lc.bind_async_lifecycle_registrar(),
        lc.bind_async_managed_lifecycle_manager(eager=True),
    ])

    #

    els.extend([
        _sessions.bind_sessions(session_cfg),

        _state.bind_state(),
    ])

    #

    els.extend([
        inj.bind(asyncs.AsyncThreadRunner, to_ctor=asyncs.AnyioAsyncThreadRunner),
    ])

    #

    return inj.as_elements(*els)
