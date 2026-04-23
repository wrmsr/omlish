import uuid

from omlish import inject as inj

from ..registries.globals import get_global_registry
from ..registries.registry import Registry
from .ai.inject import bind_ai
from .configs import DriverConfig
from .events.inject import bind_events
from .impl import DriverImpl
from .injection import placeholder_contents_providers
from .injection import system_message_providers
from .orm.inject import bind_orm
from .phases.inject import bind_phases
from .preparing.inject import bind_preparing
from .state.inject import bind_state
from .tools.inject import bind_tools
from .types import Driver
from .types import DriverGetter
from .types import DriverId
from .user.inject import bind_user


##


def bind_driver(cfg: DriverConfig = DriverConfig()) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.extend([
        bind_ai(cfg.ai),
        bind_events(),
        bind_orm(cfg.orm),
        bind_phases(),
        bind_preparing(),
        bind_state(cfg.state),
        bind_tools(cfg.tools),
        bind_user(cfg.user),
    ])

    #

    els.extend([
        system_message_providers().bind_items_provider(singleton=True),
        placeholder_contents_providers().bind_items_provider(singleton=True),
    ])

    #

    els.extend([
        inj.bind(DriverImpl, singleton=True),
        inj.bind(Driver, to_key=DriverImpl),

        inj.bind_async_late(Driver, DriverGetter),
    ])

    #

    els.append(inj.bind(DriverId(uuid.uuid4())))

    #

    els.append(inj.bind(Registry, to_const=get_global_registry()))

    #

    return inj.as_elements(*els)
