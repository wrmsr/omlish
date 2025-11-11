import typing as ta

from omlish import inject as inj
from omlish import lang


with lang.auto_proxy_import(globals()):
    from . import asyncs
    from .sessions import inject as _sessions
    from .state import inject as _state


##


def bind_main(
        *,
        session_cfg: ta.Any,
) -> inj.Elements:
    els: list[inj.Elemental] = []

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
