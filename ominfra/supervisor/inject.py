# ruff: noqa: UP006 UP007
import typing as ta

from omlish.lite.inject import InjectorBindingOrBindings
from omlish.lite.inject import InjectorBindings
from omlish.lite.inject import inj

from .configs import ServerConfig
from .context import ServerContextImpl
from .context import ServerEpoch
from .dispatchers import InputDispatcherImpl
from .dispatchers import OutputDispatcherImpl
from .events import EventCallbacks
from .groups import ProcessFactory
from .groups import ProcessGroupImpl
from .poller import Poller
from .poller import get_poller_impl
from .process import InheritedFds
from .process import InputDispatcherFactory
from .process import OutputDispatcherFactory
from .process import ProcessImpl
from .signals import SignalReceiver
from .supervisor import ProcessGroupFactory
from .supervisor import ProcessGroups
from .supervisor import SignalHandler
from .supervisor import Supervisor
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

        inj.bind_factory(ProcessGroupImpl, ProcessGroupFactory),
        inj.bind_factory(ProcessImpl, ProcessFactory),

        inj.bind_factory(OutputDispatcherImpl, OutputDispatcherFactory),
        inj.bind_factory(InputDispatcherImpl, InputDispatcherFactory),
    ]

    #

    if server_epoch is not None:
        lst.append(inj.bind(server_epoch, key=ServerEpoch))
    if inherited_fds is not None:
        lst.append(inj.bind(inherited_fds, key=InheritedFds))

    #

    return inj.as_bindings(*lst)
