import os

from omdev.home.paths import get_home_paths
from omlish import inject as inj
from omlish import lang

from ..... import minichain as mc
from ....backends.types import DefaultBackendName
from .configs import DEFAULT_BACKEND
from .configs import DriverConfig
from .printing import AiMessagesEventPrinter
from .printing import AiStreamEventPrinter
from .printing import ToolUseEventsPrinter


with lang.auto_proxy_import(globals()):
    from ....backends import inject as _backends
    from .state import inject as _state


##


def bind_driver(cfg: DriverConfig = DriverConfig()) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.extend([
        mc.drivers.inject.bind_driver(cfg),

        _state.bind_state(cfg.state),

        _backends.bind_backends(
            [
                mc.ChatChoicesStreamService,
                mc.ChatChoicesService,
            ],
            cfg.backend,
        ),
    ])

    #

    if cfg.ai.stream:
        els.extend([
            inj.bind(
                mc.ChatChoicesStreamService,
                to_fn=inj.target(
                    service_provider=mc.ServiceProvider[mc.ChatChoicesStreamService],
                )(mc.ServiceProviderProxyStreamService),
                singleton=True,
            ),
        ])

    else:
        els.extend([
            inj.bind(
                mc.ChatChoicesService,
                to_fn=inj.target(
                    service_provider=mc.ServiceProvider[mc.ChatChoicesService],
                )(mc.ServiceProviderProxyService),
                singleton=True,
            ),
        ])

    #

    els.extend([
        inj.bind(mc.SimpleToolPermissionsManager([
            mc.ToolPermissionRule(
                mc.GlobFsToolPermissionMatcher(os.path.join(os.getcwd(), '**/*'), ['r']),  # FIXME: lol
                mc.ToolPermissionState.ALLOW,
            ),
        ])),
        inj.bind(mc.ToolPermissionsManager, to_key=mc.SimpleToolPermissionsManager),
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

    els.extend([
        inj.bind(mc.drivers.EventLogger.Config, to_fn=inj.target(
            did=mc.drivers.DriverId,
        )(lambda did: mc.drivers.EventLogger.Config(
            os.path.join(get_home_paths().log_dir, 'minichain', 'drivers', f'{did.v}.jsonl'),
        ))),

        inj.bind(mc.drivers.EventLogger, singleton=True),

        mc.drivers.injection.event_callbacks().bind_item(to_fn=inj.target(o=mc.drivers.EventLogger)(lambda o: o.handle_event)),  # noqa
    ])

    #

    return inj.as_elements(*els)
