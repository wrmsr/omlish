# ruff: noqa: UP006 UP007
import signal
import time
import typing as ta

from omlish.lite.cached import cached_nullary
from omlish.lite.check import check_isinstance
from omlish.lite.check import check_not_none
from omlish.lite.logs import log
from omlish.lite.typing import Func1

from .configs import ProcessGroupConfig
from .context import ServerContextImpl
from .dispatchers import Dispatchers
from .events import TICK_EVENTS
from .events import EventCallbacks
from .events import SupervisorRunningEvent
from .events import SupervisorStoppingEvent
from .groups import ProcessGroup
from .groups import ProcessGroupManager
from .poller import Poller
from .processes import PidHistory
from .signals import SignalReceiver
from .signals import sig_name
from .states import SupervisorState
from .types import OutputDispatcher
from .types import Process
from .utils import ExitNow
from .utils import as_string
from .utils import decode_wait_status
from .utils import timeslice


##


class SignalHandler:
    def __init__(
            self,
            *,
            context: ServerContextImpl,
            signal_receiver: SignalReceiver,
            process_groups: ProcessGroupManager,
    ) -> None:
        super().__init__()

        self._context = context
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
            self._context.set_state(SupervisorState.SHUTDOWN)

        elif sig == signal.SIGHUP:
            if self._context.state == SupervisorState.SHUTDOWN:
                log.warning('ignored %s indicating restart request (shutdown in progress)', sig_name(sig))  # noqa
            else:
                log.warning('received %s indicating restart request', sig_name(sig))  # noqa
                self._context.set_state(SupervisorState.RESTARTING)

        elif sig == signal.SIGCHLD:
            log.debug('received %s indicating a child quit', sig_name(sig))

        elif sig == signal.SIGUSR2:
            log.info('received %s indicating log reopen request', sig_name(sig))

            for p in self._process_groups.all_processes():
                for d in p.get_dispatchers():
                    if isinstance(d, OutputDispatcher):
                        d.reopen_logs()

        else:
            log.debug('received %s indicating nothing', sig_name(sig))


##


class ProcessGroupFactory(Func1[ProcessGroupConfig, ProcessGroup]):
    pass


class Supervisor:
    def __init__(
            self,
            *,
            context: ServerContextImpl,
            poller: Poller,
            process_groups: ProcessGroupManager,
            signal_handler: SignalHandler,
            event_callbacks: EventCallbacks,
            process_group_factory: ProcessGroupFactory,
            pid_history: PidHistory,
    ) -> None:
        super().__init__()

        self._context = context
        self._poller = poller
        self._process_groups = process_groups
        self._signal_handler = signal_handler
        self._event_callbacks = event_callbacks
        self._process_group_factory = process_group_factory
        self._pid_history = pid_history

        self._ticks: ta.Dict[int, float] = {}
        self._stop_groups: ta.Optional[ta.List[ProcessGroup]] = None  # list used for priority ordered shutdown
        self._stopping = False  # set after we detect that we are handling a stop request
        self._last_shutdown_report = 0.  # throttle for delayed process error reports at stop

    #

    @property
    def context(self) -> ServerContextImpl:
        return self._context

    def get_state(self) -> SupervisorState:
        return self._context.state

    #

    def add_process_group(self, config: ProcessGroupConfig) -> bool:
        if self._process_groups.get(config.name) is not None:
            return False

        group = check_isinstance(self._process_group_factory(config), ProcessGroup)
        for process in group:
            process.after_setuid()

        self._process_groups.add(group)

        return True

    def remove_process_group(self, name: str) -> bool:
        if self._process_groups[name].get_unstopped_processes():
            return False

        self._process_groups.remove(name)

        return True

    #

    def shutdown_report(self) -> ta.List[Process]:
        unstopped: ta.List[Process] = []

        for group in self._process_groups:
            unstopped.extend(group.get_unstopped_processes())

        if unstopped:
            # throttle 'waiting for x to die' reports
            now = time.time()
            if now > (self._last_shutdown_report + 3):  # every 3 secs
                names = [as_string(p.config.name) for p in unstopped]
                namestr = ', '.join(names)
                log.info('waiting for %s to die', namestr)
                self._last_shutdown_report = now
                for proc in unstopped:
                    log.debug('%s state: %s', proc.config.name, proc.get_state().name)

        return unstopped

    #

    def main(self) -> None:
        self.setup()
        self.run()

    @cached_nullary
    def setup(self) -> None:
        if not self._context.first:
            # prevent crash on libdispatch-based systems, at least for the first request
            self._context.cleanup_fds()

        self._context.set_uid_or_exit()

        if self._context.first:
            self._context.set_rlimits_or_exit()

        # this sets the options.logger object delay logger instantiation until after setuid
        if not self._context.config.nocleanup:
            # clean up old automatic logs
            self._context.clear_auto_child_logdir()

    def run(
            self,
            *,
            callback: ta.Optional[ta.Callable[['Supervisor'], bool]] = None,
    ) -> None:
        self._process_groups.clear()
        self._stop_groups = None  # clear

        self._event_callbacks.clear()

        try:
            for config in self._context.config.groups or []:
                self.add_process_group(config)

            self._signal_handler.set_signals()

            if not self._context.config.nodaemon and self._context.first:
                self._context.daemonize()

            # writing pid file needs to come *after* daemonizing or pid will be wrong
            self._context.write_pidfile()

            self._event_callbacks.notify(SupervisorRunningEvent())

            while True:
                if callback is not None and not callback(self):
                    break

                self._run_once()

        finally:
            self._context.cleanup()

    #

    def _run_once(self) -> None:
        self._poll()
        self._reap()
        self._signal_handler.handle_signals()
        self._tick()

        if self._context.state < SupervisorState.RUNNING:
            self._ordered_stop_groups_phase_2()

    def _ordered_stop_groups_phase_1(self) -> None:
        if self._stop_groups:
            # stop the last group (the one with the "highest" priority)
            self._stop_groups[-1].stop_all()

    def _ordered_stop_groups_phase_2(self) -> None:
        # after phase 1 we've transitioned and reaped, let's see if we can remove the group we stopped from the
        # stop_groups queue.
        if self._stop_groups:
            # pop the last group (the one with the "highest" priority)
            group = self._stop_groups.pop()
            if group.get_unstopped_processes():
                # if any processes in the group aren't yet in a stopped state, we're not yet done shutting this group
                # down, so push it back on to the end of the stop group queue
                self._stop_groups.append(group)

    def get_dispatchers(self) -> Dispatchers:
        return Dispatchers(
            d
            for p in self._process_groups.all_processes()
            for d in p.get_dispatchers()
        )

    def _poll(self) -> None:
        dispatchers = self.get_dispatchers()

        sorted_groups = list(self._process_groups)
        sorted_groups.sort()

        if self._context.state < SupervisorState.RUNNING:
            if not self._stopping:
                # first time, set the stopping flag, do a notification and set stop_groups
                self._stopping = True
                self._stop_groups = sorted_groups[:]
                self._event_callbacks.notify(SupervisorStoppingEvent())

            self._ordered_stop_groups_phase_1()

            if not self.shutdown_report():
                # if there are no unstopped processes (we're done killing everything), it's OK to shutdown or reload
                raise ExitNow

        for fd, dispatcher in dispatchers.items():
            if dispatcher.readable():
                self._poller.register_readable(fd)
            if dispatcher.writable():
                self._poller.register_writable(fd)

        timeout = 1  # this cannot be fewer than the smallest TickEvent (5)
        r, w = self._poller.poll(timeout)

        for fd in r:
            if fd in dispatchers:
                try:
                    dispatcher = dispatchers[fd]
                    log.debug('read event caused by %r', dispatcher)
                    dispatcher.handle_read_event()
                    if not dispatcher.readable():
                        self._poller.unregister_readable(fd)
                except ExitNow:
                    raise
                except Exception:  # noqa
                    dispatchers[fd].handle_error()
            else:
                # if the fd is not in combined map, we should unregister it. otherwise, it will be polled every
                # time, which may cause 100% cpu usage
                log.debug('unexpected read event from fd %r', fd)
                try:
                    self._poller.unregister_readable(fd)
                except Exception:  # noqa
                    pass

        for fd in w:
            if fd in dispatchers:
                try:
                    dispatcher = dispatchers[fd]
                    log.debug('write event caused by %r', dispatcher)
                    dispatcher.handle_write_event()
                    if not dispatcher.writable():
                        self._poller.unregister_writable(fd)
                except ExitNow:
                    raise
                except Exception:  # noqa
                    dispatchers[fd].handle_error()
            else:
                log.debug('unexpected write event from fd %r', fd)
                try:
                    self._poller.unregister_writable(fd)
                except Exception:  # noqa
                    pass

        for group in sorted_groups:
            for process in group:
                process.transition()

    def _reap(self, *, once: bool = False, depth: int = 0) -> None:
        if depth >= 100:
            return

        pid, sts = self._context.waitpid()
        if not pid:
            return

        process = self._pid_history.get(pid, None)
        if process is None:
            _, msg = decode_wait_status(check_not_none(sts))
            log.info('reaped unknown pid %s (%s)', pid, msg)
        else:
            process.finish(check_not_none(sts))
            del self._pid_history[pid]

        if not once:
            # keep reaping until no more kids to reap, but don't recurse infinitely
            self._reap(once=False, depth=depth + 1)

    def _tick(self, now: ta.Optional[float] = None) -> None:
        """Send one or more 'tick' events when the timeslice related to the period for the event type rolls over"""

        if now is None:
            # now won't be None in unit tests
            now = time.time()

        for event in TICK_EVENTS:
            period = event.period

            last_tick = self._ticks.get(period)
            if last_tick is None:
                # we just started up
                last_tick = self._ticks[period] = timeslice(period, now)

            this_tick = timeslice(period, now)
            if this_tick != last_tick:
                self._ticks[period] = this_tick
                self._event_callbacks.notify(event(this_tick, self))
