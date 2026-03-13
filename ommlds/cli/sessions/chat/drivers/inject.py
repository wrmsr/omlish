from omlish import inject as inj

from ..... import minichain as mc
from ....backends.types import DefaultBackendName
from .configs import DEFAULT_BACKEND
from .configs import DriverConfig
from .services import ChatChoicesServiceProviderProxy
from .services import ChatChoicesStreamServiceProviderProxy


##


def bind_driver(cfg: DriverConfig = DriverConfig()) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.append(mc.drivers.inject.bind_driver(cfg))

    #

    from .state.inject import bind_state

    els.append(bind_state(cfg.state))

    #

    from ....backends.inject import bind_backends

    els.extend([
        bind_backends(cfg.backend),
    ])

    #

    if cfg.ai.stream:
        els.extend([
            inj.bind(ChatChoicesStreamServiceProviderProxy, singleton=True),
            inj.bind(mc.ChatChoicesStreamService, to_key=ChatChoicesStreamServiceProviderProxy),
            inj.bind(mc.drivers.StreamAiChatGenerator, to_ctor=mc.drivers.ChatChoicesStreamServiceStreamAiChatGenerator),
        ])

    else:
        els.extend([
            inj.bind(ChatChoicesServiceProviderProxy, singleton=True),
            inj.bind(mc.ChatChoicesService, to_key=ChatChoicesServiceProviderProxy),
            inj.bind(mc.drivers.AiChatGenerator, to_ctor=mc.drivers.ChatChoicesServiceAiChatGenerator),
        ])

    #

    els.extend([
        inj.bind(mc.DictToolPermissions, singleton=True),
        inj.bind(mc.ToolPermissions, to_key=mc.DictToolPermissions),
    ])

    #

    els.append(inj.bind(DefaultBackendName, to_const=DEFAULT_BACKEND))


    #

    if cfg.print_ai_responses:
        raise NotImplementedError

    if cfg.print_tool_executions:
        # els.append(exec_stack.push_bind(to_ctor=_printing.ArgsPrintingToolUseExecutor, singleton=True))
        # els.append(exec_stack.push_bind(to_ctor=_printing.ResultPrintingToolUseExecutor, singleton=True))
        raise NotImplementedError

    #

    return inj.as_elements(*els)
