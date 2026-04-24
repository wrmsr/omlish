import functools
import os
import typing as ta

from omdev.home.paths import get_home_paths
from omlish import inject as inj
from omlish import lang

from ..... import minichain as mc
from ....backends.injection import backend_configs
from ....backends.types import BackendConfigs
from ..backends.types import BackendSpecGetter
from .configs import DriverConfig
from .printing import AiMessagesEventPrinter
from .printing import AiStreamEventPrinter
from .printing import ToolUseEventsPrinter


with lang.auto_proxy_import(globals()):
    from .state import inject as _state


##


def bind_driver(cfg: DriverConfig = DriverConfig()) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.extend([
        mc.drivers.inject.bind_driver(cfg),

        _state.bind_state(cfg.state),
    ])

    #

    els.append(backend_configs().bind_items_provider(singleton=True))

    #

    service_cls: ta.Any
    for service_cls in [
        mc.ChatChoicesService,
        mc.ChatChoicesStreamService,
    ]:
        els.append(
            inj.bind(
                mc.ServiceProvider[service_cls],  # noqa
                to_fn=inj.target(
                    spec=BackendSpecGetter,
                    configs=BackendConfigs,
                )(functools.partial(
                    mc.BackendSpecServiceProvider,
                    service_cls,
                )),
                singleton=True,
            ),
        )

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
