# ruff: noqa: UP006 UP007
import dataclasses as dc
import typing as ta

from omlish.lite.fdio.kqueue import KqueueFdIoPoller
from omlish.lite.fdio.pollers import FdIoPoller
from omlish.lite.fdio.pollers import PollFdIoPoller
from omlish.lite.fdio.pollers import SelectFdIoPoller
from omlish.lite.inject import InjectorBindingOrBindings
from omlish.lite.inject import InjectorBindings
from omlish.lite.inject import inj

from .configs import ServerConfig
from .dispatchersimpl import ProcessInputDispatcherImpl
from .dispatchersimpl import ProcessOutputDispatcherImpl
from .events import EventCallbacks
from .groups import ProcessGroupManager
from .groupsimpl import ProcessFactory
from .groupsimpl import ProcessGroupImpl
from .io import HasDispatchersList
from .io import IoManager
from .process import PidHistory
from .processimpl import ProcessImpl
from .processimpl import ProcessSpawningFactory
from .setup import DaemonizeListener
from .setup import DaemonizeListeners
from .setup import SupervisorUser
from .setupimpl import SupervisorSetup
from .setupimpl import SupervisorSetupImpl
from .signals import SignalHandler
from .spawningimpl import InheritedFds
from .spawningimpl import ProcessInputDispatcherFactory
from .spawningimpl import ProcessOutputDispatcherFactory
from .spawningimpl import ProcessSpawningImpl
from .supervisor import ProcessGroupFactory
from .supervisor import Supervisor
from .supervisor import SupervisorStateManagerImpl
from .types import HasDispatchers
from .types import ServerEpoch
from .types import SupervisorStateManager
from .utils.signals import SignalReceiver
from .utils.users import get_user


@dc.dataclass(frozen=True)
class _FdIoPollerDaemonizeListener(DaemonizeListener):
    _poller: FdIoPoller

    def before_daemonize(self) -> None:
        self._poller.close()

    def after_daemonize(self) -> None:
        self._poller.reopen()


def bind_server(
        config: ServerConfig,
        *,
        server_epoch: ta.Optional[ServerEpoch] = None,
        inherited_fds: ta.Optional[InheritedFds] = None,
) -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = [
        inj.bind(config),

        inj.bind_array(DaemonizeListener),
        inj.bind_array_type(DaemonizeListener, DaemonizeListeners),

        inj.bind(SupervisorSetupImpl, singleton=True),
        inj.bind(SupervisorSetup, to_key=SupervisorSetupImpl),

        inj.bind(EventCallbacks, singleton=True),

        inj.bind(SignalReceiver, singleton=True),

        inj.bind(IoManager, singleton=True),
        inj.bind_array_type(HasDispatchers, HasDispatchersList),

        inj.bind(SignalHandler, singleton=True),

        inj.bind(ProcessGroupManager, singleton=True),
        inj.bind(HasDispatchers, array=True, to_key=ProcessGroupManager),

        inj.bind(Supervisor, singleton=True),

        inj.bind(SupervisorStateManagerImpl, singleton=True),
        inj.bind(SupervisorStateManager, to_key=SupervisorStateManagerImpl),

        inj.bind(PidHistory()),

        inj.bind_factory(ProcessGroupImpl, ProcessGroupFactory),
        inj.bind_factory(ProcessImpl, ProcessFactory),

        inj.bind_factory(ProcessSpawningImpl, ProcessSpawningFactory),

        inj.bind_factory(ProcessOutputDispatcherImpl, ProcessOutputDispatcherFactory),
        inj.bind_factory(ProcessInputDispatcherImpl, ProcessInputDispatcherFactory),
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

    poller_impl = next(filter(None, [
        # KqueueFdIoPoller,
        # PollFdIoPoller,
        SelectFdIoPoller,
    ]))
    lst.append(inj.bind(poller_impl, key=FdIoPoller, singleton=True))
    inj.bind(_FdIoPollerDaemonizeListener, array=True, singleton=True)

    #

    return inj.as_bindings(*lst)
