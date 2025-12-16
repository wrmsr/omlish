"""
TODO:
 - private + expose(ChatAgent)
"""
from omlish import inject as inj
from omlish import lang

from ....backends.types import DefaultBackendName
from .configs import DEFAULT_BACKEND
from .configs import AgentConfig


with lang.auto_proxy_import(globals()):
    from ....backends import inject as _backends
    from . import agent as _agent
    from . import events as _events
    from .ai import inject as _ai
    from .phases import inject as _phases
    from .state import inject as _state
    from .tools import inject as _tools
    from .user import inject as _user


##


def bind_agent(cfg: AgentConfig) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.extend([
        _backends.bind_backends(cfg.backend),

        _ai.bind_ai(cfg.ai),

        _phases.bind_phases(),

        _state.bind_state(cfg.state),

        _tools.bind_tools(cfg.tools),

        _user.bind_user(cfg.user),
    ])

    #

    els.extend([
        inj.bind(_agent.ChatAgent, singleton=True),

        inj.bind_late(_agent.ChatAgent),
    ])

    #

    # FIXME:
    els.extend([
        inj.bind(_events.ChatAgentEventSink, to_const=lang.as_async(lambda e: None)),  # type: ignore[misc]
    ])

    #

    els.append(inj.bind(DefaultBackendName, to_const=DEFAULT_BACKEND))

    #

    return inj.as_elements(*els)
