# ruff: noqa: UP006 UP007
import dataclasses as dc
import signal
import time
import typing as ta

from omlish.lite.cached import cached_nullary
from omlish.lite.check import check_not_none
from omlish.lite.logs import log

from .compat import ExitNow
from .compat import as_string
from .compat import decode_wait_status
from .compat import signame
from .configs import ProcessGroupConfig
from .context import ServerContext
from .dispatchers import Dispatcher
from .events import EVENT_CALLBACKS
from .events import TICK_EVENTS
from .events import ProcessGroupAddedEvent
from .events import ProcessGroupRemovedEvent
from .events import SupervisorRunningEvent
from .events import SupervisorStoppingEvent
from .process import ProcessGroup
from .process import Subprocess
from .states import SupervisorState
from .states import SupervisorStates
from .states import get_process_state_description


def timeslice(period: int, when: float) -> int:
    return int(when - (when % period))


@dc.dataclass(frozen=True)
class ProcessGroupFactory:
    fn: ta.Callable[[ProcessGroupConfig], ProcessGroup]

    def __call__(self, config: ProcessGroupConfig) -> ProcessGroup:
        return self.fn(config)


class Supervisor:

    def __init__(
            self,
            context: ServerContext,
            *,
            process_group_factory: ta.Optional[ProcessGroupFactory] = None,
    ) -> None:
        super().__init__()

        self._context = context

        if process_group_factory is None:
            def make_process_group(config: ProcessGroupConfig) -> ProcessGroup:
                return ProcessGroup(config, self._context)
            process_group_factory = ProcessGroupFactory(make_process_group)
        self._process_group_factory = process_group_factory

        self._ticks: ta.Dict[int, float] = {}
        self._process_groups: ta.Dict[str, ProcessGroup] = {}  # map of process group name to process group object
        self._stop_groups: ta.Optional[ta.List[ProcessGroup]] = None  # list used for priority ordered shutdown
        self._stopping = False  # set after we detect that we are handling a stop request
        self._last_shutdown_report = 0.  # throttle for delayed process error reports at stop

    #

    @property
    def context(self) -> ServerContext:
        return self._context

    def get_state(self) -> SupervisorState:
        return self._context.state

    #

    class DiffToActive(ta.NamedTuple):
        added: ta.List[ProcessGroupConfig]
        changed: ta.List[ProcessGroupConfig]
        removed: ta.List[ProcessGroupConfig]

    def diff_to_active(self) -> DiffToActive:
        new = self._context.config.groups or []
        cur = [group.config for group in self._process_groups.values()]

        curdict = dict(zip([cfg.name for cfg in cur], cur))
        newdict = dict(zip([cfg.name for cfg in new], new))

        added = [cand for cand in new if cand.name not in curdict]
        removed = [cand for cand in cur if cand.name not in newdict]

        changed = [cand for cand in new if cand != curdict.get(cand.name, cand)]

        return Supervisor.DiffToActive(added, changed, removed)

    def add_process_group(self, config: ProcessGroupConfig) -> bool:
        name = config.name
        if name in self._process_groups:
            return False

        group = self._process_groups[name] = self._process_group_factory(config)
        group.after_setuid()

        EVENT_CALLBACKS.notify(ProcessGroupAddedEvent(name))
        return True

    def remove_process_group(self, name: str) -> bool:
        if self._process_groups[name].get_unstopped_processes():
            return False

        self._process_groups[name].before_remove()

        del self._process_groups[name]

        EVENT_CALLBACKS.notify(ProcessGroupRemovedEvent(name))
        return True

    def get_process_map(self) -> ta.Dict[int, Dispatcher]:
        process_map = {}
        for group in self._process_groups.values():
            process_map.update(group.get_dispatchers())
        return process_map

    def shutdown_report(self) -> ta.List[Subprocess]:
        unstopped: ta.List[Subprocess] = []

        for group in self._process_groups.values():
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
                    state = get_process_state_description(proc.get_state())
                    log.debug('%s state: %s', proc.config.name, state)

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
        self._process_groups = {}  # clear
        self._stop_groups = None  # clear

        EVENT_CALLBACKS.clear()

        try:
            for config in self._context.config.groups or []:
                self.add_process_group(config)

            self._context.set_signals()

            if not self._context.config.nodaemon and self._context.first:
                self._context.daemonize()

            # writing pid file needs to come *after* daemonizing or pid will be wrong
            self._context.write_pidfile()

            EVENT_CALLBACKS.notify(SupervisorRunningEvent())

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
        self._handle_signal()
        self._tick()

        if self._context.state < SupervisorStates.RUNNING:
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

    def _poll(self) -> None:
        combined_map = {}
        combined_map.update(self.get_process_map())

        pgroups = list(self._process_groups.values())
        pgroups.sort()

        if self._context.state < SupervisorStates.RUNNING:
            if not self._stopping:
                # first time, set the stopping flag, do a notification and set stop_groups
                self._stopping = True
                self._stop_groups = pgroups[:]
                EVENT_CALLBACKS.notify(SupervisorStoppingEvent())

            self._ordered_stop_groups_phase_1()

            if not self.shutdown_report():
                # if there are no unstopped processes (we're done killing everything), it's OK to shutdown or reload
                raise ExitNow

        for fd, dispatcher in combined_map.items():
            if dispatcher.readable():
                self._context.poller.register_readable(fd)
            if dispatcher.writable():
                self._context.poller.register_writable(fd)

        timeout = 1  # this cannot be fewer than the smallest TickEvent (5)
        r, w = self._context.poller.poll(timeout)

        for fd in r:
            if fd in combined_map:
                try:
                    dispatcher = combined_map[fd]
                    log.debug('read event caused by %r', dispatcher)
                    dispatcher.handle_read_event()
                    if not dispatcher.readable():
                        self._context.poller.unregister_readable(fd)
                except ExitNow:
                    raise
                except Exception:  # noqa
                    combined_map[fd].handle_error()
            else:
                # if the fd is not in combined_map, we should unregister it. otherwise, it will be polled every
                # time, which may cause 100% cpu usage
                log.debug('unexpected read event from fd %r', fd)
                try:
                    self._context.poller.unregister_readable(fd)
                except Exception:  # noqa
                    pass

        for fd in w:
            if fd in combined_map:
                try:
                    dispatcher = combined_map[fd]
                    log.debug('write event caused by %r', dispatcher)
                    dispatcher.handle_write_event()
                    if not dispatcher.writable():
                        self._context.poller.unregister_writable(fd)
                except ExitNow:
                    raise
                except Exception:  # noqa
                    combined_map[fd].handle_error()
            else:
                log.debug('unexpected write event from fd %r', fd)
                try:
                    self._context.poller.unregister_writable(fd)
                except Exception:  # noqa
                    pass

        for group in pgroups:
            group.transition()

    def _reap(self, *, once: bool = False, depth: int = 0) -> None:
        if depth >= 100:
            return

        pid, sts = self._context.waitpid()
        if not pid:
            return

        process = self._context.pid_history.get(pid, None)
        if process is None:
            _, msg = decode_wait_status(check_not_none(sts))
            log.info('reaped unknown pid %s (%s)', pid, msg)
        else:
            process.finish(check_not_none(sts))
            del self._context.pid_history[pid]

        if not once:
            # keep reaping until no more kids to reap, but don't recurse infinitely
            self._reap(once=False, depth=depth + 1)

    def _handle_signal(self) -> None:
        sig = self._context.get_signal()
        if not sig:
            return

        if sig in (signal.SIGTERM, signal.SIGINT, signal.SIGQUIT):
            log.warning('received %s indicating exit request', signame(sig))
            self._context.set_state(SupervisorStates.SHUTDOWN)

        elif sig == signal.SIGHUP:
            if self._context.state == SupervisorStates.SHUTDOWN:
                log.warning('ignored %s indicating restart request (shutdown in progress)', signame(sig))  # noqa
            else:
                log.warning('received %s indicating restart request', signame(sig))  # noqa
                self._context.set_state(SupervisorStates.RESTARTING)

        elif sig == signal.SIGCHLD:
            log.debug('received %s indicating a child quit', signame(sig))

        elif sig == signal.SIGUSR2:
            log.info('received %s indicating log reopen request', signame(sig))
            # self._context.reopen_logs()
            for group in self._process_groups.values():
                group.reopen_logs()

        else:
            log.debug('received %s indicating nothing', signame(sig))

    def _tick(self, now: ta.Optional[float] = None) -> None:
        """Send one or more 'tick' events when the timeslice related to the period for the event type rolls over"""

        if now is None:
            # now won't be None in unit tests
            now = time.time()

        for event in TICK_EVENTS:
            period = event.period  # type: ignore

            last_tick = self._ticks.get(period)
            if last_tick is None:
                # we just started up
                last_tick = self._ticks[period] = timeslice(period, now)

            this_tick = timeslice(period, now)
            if this_tick != last_tick:
                self._ticks[period] = this_tick
                EVENT_CALLBACKS.notify(event(this_tick, self))
