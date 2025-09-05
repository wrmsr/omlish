# ruff: noqa: UP006 UP007 UP045
import signal

from omlish.logs.modules import get_module_logger

from .groups import ProcessGroupManager
from .states import SupervisorState
from .types import ProcessOutputDispatcher
from .types import SupervisorStateManager
from .utils.signals import SignalReceiver
from .utils.signals import sig_name


log = get_module_logger(globals())  # noqa


##


class SignalHandler:
    def __init__(
            self,
            *,
            states: SupervisorStateManager,
            signal_receiver: SignalReceiver,
            process_groups: ProcessGroupManager,
    ) -> None:
        super().__init__()

        self._states = states
        self._signal_receiver = signal_receiver
        self._process_groups = process_groups

    def set_signals(self) -> None:
        self._signal_receiver.install(
            signal.SIGTERM,
            signal.SIGINT,
            signal.SIGQUIT,
            signal.SIGHUP,
            signal.SIGCHLD,
            signal.SIGUSR2,
        )

    def handle_signals(self) -> None:
        sig = self._signal_receiver.get_signal()
        if not sig:
            return

        if sig in (signal.SIGTERM, signal.SIGINT, signal.SIGQUIT):
            log.warning('received %s indicating exit request', sig_name(sig))
            self._states.set_state(SupervisorState.SHUTDOWN)

        elif sig == signal.SIGHUP:
            if self._states.state == SupervisorState.SHUTDOWN:
                log.warning('ignored %s indicating restart request (shutdown in progress)', sig_name(sig))  # noqa
            else:
                log.warning('received %s indicating restart request', sig_name(sig))  # noqa
                self._states.set_state(SupervisorState.RESTARTING)

        elif sig == signal.SIGCHLD:
            log.debug('received %s indicating a child quit', sig_name(sig))

        elif sig == signal.SIGUSR2:
            log.info('received %s indicating log reopen request', sig_name(sig))

            for p in self._process_groups.all_processes():
                for d in p.get_dispatchers():
                    if isinstance(d, ProcessOutputDispatcher):
                        d.reopen_logs()

        else:
            log.debug('received %s indicating nothing', sig_name(sig))
