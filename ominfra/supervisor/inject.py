# ruff: noqa: UP006 UP007
import typing as ta

from omlish.lite.inject import InjectorBindingOrBindings
from omlish.lite.inject import InjectorBindings
from omlish.lite.inject import inj

from .configs import ServerConfig
from .context import ServerContextImpl
from .dispatchersimpl import InputDispatcherImpl
from .dispatchersimpl import OutputDispatcherImpl
from .events import EventCallbacks
from .groups import ProcessGroupManager
from .groupsimpl import ProcessFactory
from .groupsimpl import ProcessGroupImpl
from .poller import Poller
from .poller import get_poller_impl
from .process import PidHistory
from .processimpl import ProcessImpl
from .processimpl import ProcessSpawningFactory
from .setup import DaemonizeListener
from .setup import DaemonizeListeners
from .setup import SupervisorUser
from .setupimpl import SupervisorSetup
from .setupimpl import SupervisorSetupImpl
from .spawningimpl import InheritedFds
from .spawningimpl import InputDispatcherFactory
from .spawningimpl import OutputDispatcherFactory
from .spawningimpl import ProcessSpawningImpl
from .supervisor import ProcessGroupFactory
from .supervisor import SignalHandler
from .supervisor import Supervisor
from .types import ServerContext
from .types import ServerEpoch
from .utils.signals import SignalReceiver
from .utils.users import get_user


def bind_server(
        config: ServerConfig,
        *,
        server_epoch: ta.Optional[ServerEpoch] = None,
        inherited_fds: ta.Optional[InheritedFds] = None,
) -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = [
        inj.bind(config),

        inj.bind_array_type(DaemonizeListener, DaemonizeListeners),

        inj.bind(SupervisorSetupImpl, singleton=True),
        inj.bind(SupervisorSetup, to_key=SupervisorSetupImpl),

        inj.bind(DaemonizeListener, array=True, to_key=Poller),

        inj.bind(ServerContextImpl, singleton=True),
        inj.bind(ServerContext, to_key=ServerContextImpl),

        inj.bind(EventCallbacks, singleton=True),

        inj.bind(SignalReceiver, singleton=True),

        inj.bind(SignalHandler, singleton=True),
        inj.bind(ProcessGroupManager, singleton=True),
        inj.bind(Supervisor, singleton=True),

        inj.bind(PidHistory()),

        inj.bind_factory(ProcessGroupImpl, ProcessGroupFactory),
        inj.bind_factory(ProcessImpl, ProcessFactory),

        inj.bind_factory(ProcessSpawningImpl, ProcessSpawningFactory),

        inj.bind_factory(OutputDispatcherImpl, OutputDispatcherFactory),
        inj.bind_factory(InputDispatcherImpl, InputDispatcherFactory),
    ]

    #

    if server_epoch is not None:
        lst.append(inj.bind(server_epoch, key=ServerEpoch))
    if inherited_fds is not None:
        lst.append(inj.bind(inherited_fds, key=InheritedFds))

    #

    if config.user is not None:
        user = get_user(config.user)
        lst.append(inj.bind(user, key=SupervisorUser))

    #

    lst.append(inj.bind(get_poller_impl(), key=Poller, singleton=True))

    #

    return inj.as_bindings(*lst)
