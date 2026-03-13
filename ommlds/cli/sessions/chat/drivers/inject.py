from omlish import inject as inj

from ..... import minichain as mc
from ....backends.types import DefaultBackendName
from .configs import DEFAULT_BACKEND
from .configs import DriverConfig
from .printing import AiMessagesEventPrinter
from .printing import AiStreamEventPrinter
from .printing import ToolUseEventsPrinter
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
        ])

    else:
        els.extend([
            inj.bind(ChatChoicesServiceProviderProxy, singleton=True),
            inj.bind(mc.ChatChoicesService, to_key=ChatChoicesServiceProviderProxy),
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
        if cfg.ai.stream:
            els.extend([
                inj.bind(AiStreamEventPrinter, singleton=True),

                mc.drivers.injection.event_callbacks().bind_item(to_fn=inj.target(o=AiStreamEventPrinter)(lambda o: o.handle_event)),  # noqa
            ])

        else:
            els.extend([
                inj.bind(AiMessagesEventPrinter, singleton=True),

                mc.drivers.injection.event_callbacks().bind_item(to_fn=inj.target(o=AiMessagesEventPrinter)(lambda o: o.handle_event)),  # noqa
            ])

    if cfg.print_tool_use:
        els.extend([
            inj.bind(ToolUseEventsPrinter, singleton=True),

            mc.drivers.injection.event_callbacks().bind_item(to_fn=inj.target(o=ToolUseEventsPrinter)(lambda o: o.handle_event)),  # noqa
        ])

    #

    return inj.as_elements(*els)
