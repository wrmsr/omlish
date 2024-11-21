# ruff: noqa: UP006 UP007
import functools
import typing as ta

from omlish.lite.inject import Injector
from omlish.lite.inject import InjectorBindingOrBindings
from omlish.lite.inject import InjectorBindings
from omlish.lite.inject import inj

from .configs import ProcessConfig
from .configs import ProcessGroupConfig
from .configs import ServerConfig
from .context import ServerContextImpl
from .context import ServerEpoch
from .events import EventCallbacks
from .groups import ProcessFactory
from .groups import ProcessGroupImpl
from .poller import Poller
from .poller import get_poller_impl
from .process import InheritedFds
from .process import ProcessImpl
from .signals import SignalReceiver
from .supervisor import ProcessGroupFactory
from .supervisor import ProcessGroups
from .supervisor import SignalHandler
from .supervisor import Supervisor
from .types import Process
from .types import ProcessGroup
from .types import ServerContext


##


def bind_server(
        config: ServerConfig,
        *,
        server_epoch: ta.Optional[ServerEpoch] = None,
        inherited_fds: ta.Optional[InheritedFds] = None,
) -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = [
        inj.bind(config),

        inj.bind(get_poller_impl(), key=Poller, singleton=True),

        inj.bind(ServerContextImpl, singleton=True),
        inj.bind(ServerContext, to_key=ServerContextImpl),

        inj.bind(EventCallbacks, singleton=True),

        inj.bind(SignalReceiver, singleton=True),

        inj.bind(SignalHandler, singleton=True),
        inj.bind(ProcessGroups, singleton=True),
        inj.bind(Supervisor, singleton=True),
    ]

    #

    def make_process_group_factory(injector: Injector) -> ProcessGroupFactory:
        def inner(group_config: ProcessGroupConfig) -> ProcessGroup:
            return injector.inject(functools.partial(ProcessGroupImpl, group_config))
        return ProcessGroupFactory(inner)
    lst.append(inj.bind(make_process_group_factory))

    def make_process_factory(injector: Injector) -> ProcessFactory:
        def inner(process_config: ProcessConfig, group: ProcessGroup) -> Process:
            return injector.inject(functools.partial(ProcessImpl, process_config, group))
        return ProcessFactory(inner)
    lst.append(inj.bind(make_process_factory))

    #

    if server_epoch is not None:
        lst.append(inj.bind(server_epoch, key=ServerEpoch))
    if inherited_fds is not None:
        lst.append(inj.bind(inherited_fds, key=InheritedFds))

    #

    return inj.as_bindings(*lst)
