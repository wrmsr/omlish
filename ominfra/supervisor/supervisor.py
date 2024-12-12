# ruff: noqa: UP006 UP007
import time
import typing as ta

from omlish.io.fdio.pollers import FdioPoller
from omlish.lite.check import check
from omlish.lite.logs import log
from omlish.lite.typing import Func1

from .configs import ProcessGroupConfig
from .configs import ServerConfig
from .events import TICK_EVENTS
from .events import EventCallbacks
from .events import SupervisorRunningEvent
from .events import SupervisorStoppingEvent
from .groups import ProcessGroup
from .groups import ProcessGroupManager
from .io import IoManager
from .process import PidHistory
from .setup import SupervisorSetup
from .signals import SignalHandler
from .states import SupervisorState
from .types import ExitNow
from .types import Process
from .types import SupervisorStateManager
from .utils.os import decode_wait_status
from .utils.os import waitpid


##


def timeslice(period: int, when: float) -> int:
    return int(when - (when % period))


##


class SupervisorStateManagerImpl(SupervisorStateManager):
    def __init__(self) -> None:
        super().__init__()

        self._state: SupervisorState = SupervisorState.RUNNING

    @property
    def state(self) -> SupervisorState:
        return self._state

    def set_state(self, state: SupervisorState) -> None:
        self._state = state


##


class ProcessGroupFactory(Func1[ProcessGroupConfig, ProcessGroup]):
    pass


class Supervisor:
    def __init__(
            self,
            *,
            config: ServerConfig,
            poller: FdioPoller,
            process_groups: ProcessGroupManager,
            signal_handler: SignalHandler,
            event_callbacks: EventCallbacks,
            process_group_factory: ProcessGroupFactory,
            pid_history: PidHistory,
            setup: SupervisorSetup,
            states: SupervisorStateManager,
            io: IoManager,
    ) -> None:
        super().__init__()

        self._config = config
        self._poller = poller
        self._process_groups = process_groups
        self._signal_handler = signal_handler
        self._event_callbacks = event_callbacks
        self._process_group_factory = process_group_factory
        self._pid_history = pid_history
        self._setup = setup
        self._states = states
        self._io = io

        self._ticks: ta.Dict[int, float] = {}
        self._stop_groups: ta.Optional[ta.List[ProcessGroup]] = None  # list used for priority ordered shutdown
        self._stopping = False  # set after we detect that we are handling a stop request
        self._last_shutdown_report = 0.  # throttle for delayed process error reports at stop

    #

    @property
    def state(self) -> SupervisorState:
        return self._states.state

    #

    def add_process_group(self, config: ProcessGroupConfig) -> bool:
        if self._process_groups.get(config.name) is not None:
            return False

        group = check.isinstance(self._process_group_factory(config), ProcessGroup)
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
                names = [p.config.name for p in unstopped]
                namestr = ', '.join(names)
                log.info('waiting for %s to die', namestr)
                self._last_shutdown_report = now
                for proc in unstopped:
                    log.debug('%s state: %s', proc.config.name, proc.state.name)

        return unstopped

    #

    def main(self, **kwargs: ta.Any) -> None:
        self._setup.setup()
        try:
            self.run(**kwargs)
        finally:
            self._setup.cleanup()

    def run(
            self,
            *,
            callback: ta.Optional[ta.Callable[['Supervisor'], bool]] = None,
    ) -> None:
        self._process_groups.clear()
        self._stop_groups = None  # clear

        self._event_callbacks.clear()

        try:
            for config in self._config.groups or []:
                self.add_process_group(config)

            self._signal_handler.set_signals()

            self._event_callbacks.notify(SupervisorRunningEvent())

            while True:
                if callback is not None and not callback(self):
                    break

                self._run_once()

        finally:
            self._poller.close()

    #

    def _run_once(self) -> None:
        if self._states.state < SupervisorState.RUNNING:
            if not self._stopping:
                # first time, set the stopping flag, do a notification and set stop_groups
                self._stopping = True
                self._stop_groups = sorted(self._process_groups)
                self._event_callbacks.notify(SupervisorStoppingEvent())

            self._ordered_stop_groups_phase_1()

            if not self.shutdown_report():
                # if there are no unstopped processes (we're done killing everything), it's OK to shutdown or reload
                raise ExitNow

        self._io.poll()

        for group in sorted(self._process_groups):
            for process in group:
                process.transition()

        self._reap()

        self._signal_handler.handle_signals()

        self._tick()

        if self._states.state < SupervisorState.RUNNING:
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

    #

    def _reap(self, *, once: bool = False, depth: int = 0) -> None:
        if depth >= 100:
            return

        wp = waitpid(log=log)

        if wp is None or not wp.pid:
            return

        log.info(f'Waited pid: {wp}')  # noqa
        process = self._pid_history.get(wp.pid, None)
        if process is None:
            _, msg = decode_wait_status(wp.sts)
            log.info('reaped unknown pid %s (%s)', wp.pid, msg)
        else:
            process.finish(wp.sts)
            del self._pid_history[wp.pid]

        if not once:
            # keep reaping until no more kids to reap, but don't recurse infinitely
            self._reap(once=False, depth=depth + 1)

    #

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
