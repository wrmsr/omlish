# ruff: noqa: UP006 UP007
import errno
import os.path
import signal
import time
import traceback
import typing as ta

from omlish.lite.check import check
from omlish.lite.logs import log
from omlish.lite.typing import Func1

from .configs import ProcessConfig
from .configs import RestartUnconditionally
from .dispatchers import Dispatchers
from .events import PROCESS_STATE_EVENT_MAP
from .events import EventCallbacks
from .pipes import ProcessPipes
from .pipes import close_parent_pipes
from .process import ProcessStateError
from .spawning import ProcessSpawnError
from .spawning import ProcessSpawning
from .states import ProcessState
from .states import SupervisorState
from .types import Process
from .types import ProcessGroup
from .types import ProcessInputDispatcher
from .types import SupervisorStateManager
from .utils.os import decode_wait_status
from .utils.ostypes import Pid
from .utils.ostypes import Rc
from .utils.signals import sig_name


class ProcessSpawningFactory(Func1[Process, ProcessSpawning]):
    pass


##


class ProcessImpl(Process):
    """A class to manage a subprocess."""

    def __init__(
            self,
            config: ProcessConfig,
            group: ProcessGroup,
            *,
            supervisor_states: SupervisorStateManager,
            event_callbacks: EventCallbacks,
            process_spawning_factory: ProcessSpawningFactory,
    ) -> None:
        super().__init__()

        self._config = config
        self._group = group

        self._supervisor_states = supervisor_states
        self._event_callbacks = event_callbacks

        self._spawning = process_spawning_factory(self)

        #

        self._dispatchers = Dispatchers([])
        self._pipes = ProcessPipes()

        self._state = ProcessState.STOPPED
        self._pid = Pid(0)  # 0 when not running

        self._last_start = 0.  # Last time the subprocess was started; 0 if never
        self._last_stop = 0.  # Last time the subprocess was stopped; 0 if never
        self._last_stop_report = 0.  # Last time "waiting for x to stop" logged, to throttle
        self._delay = 0.  # If nonzero, delay starting or killing until this time

        self._administrative_stop = False  # true if process has been stopped by an admin
        self._system_stop = False  # true if process has been stopped by the system

        self._killing = False  # true if we are trying to kill this process

        self._backoff = 0  # backoff counter (to start_retries)

        self._exitstatus: ta.Optional[Rc] = None  # status attached to dead process by finish()
        self._spawn_err: ta.Optional[str] = None  # error message attached by _spawn() if any

    #

    def __repr__(self) -> str:
        return f'<Subprocess at {id(self)} with name {self._config.name} in state {self._state.name}>'

    #

    @property
    def name(self) -> str:
        return self._config.name

    @property
    def config(self) -> ProcessConfig:
        return self._config

    @property
    def group(self) -> ProcessGroup:
        return self._group

    @property
    def pid(self) -> Pid:
        return self._pid

    #

    @property
    def state(self) -> ProcessState:
        return self._state

    @property
    def backoff(self) -> int:
        return self._backoff

    #

    def _spawn(self) -> ta.Optional[Pid]:
        if self.pid:
            log.warning('process \'%s\' already running', self.name)
            return None

        self._check_in_state(
            ProcessState.EXITED,
            ProcessState.FATAL,
            ProcessState.BACKOFF,
            ProcessState.STOPPED,
        )

        self._killing = False
        self._spawn_err = None
        self._exitstatus = None
        self._system_stop = False
        self._administrative_stop = False

        self._last_start = time.time()

        self._change_state(ProcessState.STARTING)

        try:
            sp = self._spawning.spawn()
        except ProcessSpawnError as err:
            log.exception('Spawn error')
            self._spawn_err = err.args[0]
            self._check_in_state(ProcessState.STARTING)
            self._change_state(ProcessState.BACKOFF)
            return None

        log.info("Spawned: '%s' with pid %s", self.name, sp.pid)

        self._pid = sp.pid
        self._pipes = sp.pipes
        self._dispatchers = sp.dispatchers

        self._delay = time.time() + self.config.start_secs

        return sp.pid

    def get_dispatchers(self) -> Dispatchers:
        return self._dispatchers

    def write(self, chars: ta.Union[bytes, str]) -> None:
        if not self.pid or self._killing:
            raise OSError(errno.EPIPE, 'Process already closed')

        stdin_fd = self._pipes.stdin
        if stdin_fd is None:
            raise OSError(errno.EPIPE, 'Process has no stdin channel')

        dispatcher = check.isinstance(self._dispatchers[stdin_fd], ProcessInputDispatcher)
        if dispatcher.closed:
            raise OSError(errno.EPIPE, "Process' stdin channel is closed")

        dispatcher.write(chars)
        dispatcher.flush()  # this must raise EPIPE if the pipe is closed

    #

    def _change_state(self, new_state: ProcessState, expected: bool = True) -> bool:
        old_state = self._state
        if new_state is old_state:
            return False

        self._state = new_state
        if new_state == ProcessState.BACKOFF:
            now = time.time()
            self._backoff += 1
            self._delay = now + self._backoff

        event_class = PROCESS_STATE_EVENT_MAP.get(new_state)
        if event_class is not None:
            event = event_class(self, old_state, expected)
            self._event_callbacks.notify(event)

        return True

    def _check_in_state(self, *states: ProcessState) -> None:
        if self._state not in states:
            raise ProcessStateError(
                f'Check failed for {self._config.name}: '
                f'{self._state.name} not in {" ".join(s.name for s in states)}',
            )

    #

    def _check_and_adjust_for_system_clock_rollback(self, test_time: float) -> None:
        """
        Check if system clock has rolled backward beyond test_time. If so, set affected timestamps to test_time.
        """

        if self._state == ProcessState.STARTING:
            self._last_start = min(test_time, self._last_start)
            if self._delay > 0 and test_time < (self._delay - self._config.start_secs):
                self._delay = test_time + self._config.start_secs

        elif self._state == ProcessState.RUNNING:
            if test_time > self._last_start and test_time < (self._last_start + self._config.start_secs):
                self._last_start = test_time - self._config.start_secs

        elif self._state == ProcessState.STOPPING:
            self._last_stop_report = min(test_time, self._last_stop_report)
            if self._delay > 0 and test_time < (self._delay - self._config.stop_wait_secs):
                self._delay = test_time + self._config.stop_wait_secs

        elif self._state == ProcessState.BACKOFF:
            if self._delay > 0 and test_time < (self._delay - self._backoff):
                self._delay = test_time + self._backoff

    def stop(self) -> ta.Optional[str]:
        self._administrative_stop = True
        self._last_stop_report = 0
        return self.kill(self._config.stop_signal)

    def stop_report(self) -> None:
        """Log a 'waiting for x to stop' message with throttling."""

        if self._state == ProcessState.STOPPING:
            now = time.time()

            self._check_and_adjust_for_system_clock_rollback(now)

            if now > (self._last_stop_report + 2):  # every 2 seconds
                log.info('waiting for %s to stop', self.name)
                self._last_stop_report = now

    def give_up(self) -> None:
        self._delay = 0
        self._backoff = 0
        self._system_stop = True
        self._check_in_state(ProcessState.BACKOFF)
        self._change_state(ProcessState.FATAL)

    def kill(self, sig: int) -> ta.Optional[str]:
        """
        Send a signal to the subprocess with the intention to kill it (to make it exit). This may or may not actually
        kill it.

        Return None if the signal was sent, or an error message string if an error occurred or if the subprocess is not
        running.
        """

        now = time.time()

        # If the process is in BACKOFF and we want to stop or kill it, then BACKOFF -> STOPPED. This is needed because
        # if start_retries is a large number and the process isn't starting successfully, the stop request would be
        # blocked for a long time waiting for the retries.
        if self._state == ProcessState.BACKOFF:
            log.debug('Attempted to kill %s, which is in BACKOFF state.', self.name)
            self._change_state(ProcessState.STOPPED)
            return None

        args: tuple
        if not self.pid:
            fmt, args = "attempted to kill %s with sig %s but it wasn't running", (self.name, sig_name(sig))
            log.debug(fmt, *args)
            return fmt % args

        # If we're in the stopping state, then we've already sent the stop signal and this is the kill signal
        if self._state == ProcessState.STOPPING:
            kill_as_group = self._config.kill_as_group
        else:
            kill_as_group = self._config.stop_as_group

        as_group = ''
        if kill_as_group:
            as_group = 'process group '

        log.debug('killing %s (pid %s) %s with signal %s', self.name, self.pid, as_group, sig_name(sig))

        # RUNNING/STARTING/STOPPING -> STOPPING
        self._killing = True
        self._delay = now + self._config.stop_wait_secs
        # we will already be in the STOPPING state if we're doing a SIGKILL as a result of overrunning stop_wait_secs
        self._check_in_state(ProcessState.RUNNING, ProcessState.STARTING, ProcessState.STOPPING)
        self._change_state(ProcessState.STOPPING)

        kpid = int(self.pid)
        if kill_as_group:
            # send to the whole process group instead
            kpid = -kpid

        try:
            try:
                os.kill(kpid, sig)
            except OSError as exc:
                if exc.errno == errno.ESRCH:
                    log.debug('unable to signal %s (pid %s), it probably just exited on its own: %s', self.name, self.pid, str(exc))  # noqa
                    # we could change the state here but we intentionally do not. we will do it during normal SIGCHLD
                    # processing.
                    return None
                raise
        except Exception:  # noqa
            tb = traceback.format_exc()
            fmt, args = 'unknown problem killing %s (%s):%s', (self.name, self.pid, tb)
            log.critical(fmt, *args)
            self._change_state(ProcessState.UNKNOWN)
            self._killing = False
            self._delay = 0
            return fmt % args

        return None

    def signal(self, sig: int) -> ta.Optional[str]:
        """
        Send a signal to the subprocess, without intending to kill it.

        Return None if the signal was sent, or an error message string if an error occurred or if the subprocess is not
        running.
        """
        args: tuple
        if not self.pid:
            fmt, args = "Attempted to send %s sig %s but it wasn't running", (self.name, sig_name(sig))
            log.debug(fmt, *args)
            return fmt % args

        log.debug('sending %s (pid %s) sig %s', self.name, self.pid, sig_name(sig))

        self._check_in_state(ProcessState.RUNNING, ProcessState.STARTING, ProcessState.STOPPING)

        try:
            try:
                os.kill(self.pid, sig)
            except OSError as exc:
                if exc.errno == errno.ESRCH:
                    log.debug(
                        'unable to signal %s (pid %s), it probably just now exited on its own: %s',
                        self.name,
                        self.pid,
                        str(exc),
                    )
                    # we could change the state here but we intentionally do not. we will do it during normal SIGCHLD
                    # processing.
                    return None
                raise
        except Exception:  # noqa
            tb = traceback.format_exc()
            fmt, args = 'unknown problem sending sig %s (%s):%s', (self.name, self.pid, tb)
            log.critical(fmt, *args)
            self._change_state(ProcessState.UNKNOWN)
            return fmt % args

        return None

    def finish(self, sts: Rc) -> None:
        """The process was reaped and we need to report and manage its state."""

        self._dispatchers.drain()

        es, msg = decode_wait_status(sts)

        now = time.time()

        self._check_and_adjust_for_system_clock_rollback(now)

        self._last_stop = now

        if now > self._last_start:
            too_quickly = now - self._last_start < self._config.start_secs
        else:
            too_quickly = False
            log.warning(
                "process '%s' (%s) last_start time is in the future, don't know how long process was running so "
                "assuming it did not exit too quickly",
                self.name,
                self.pid,
            )

        exit_expected = es in self._config.exitcodes

        if self._killing:
            # likely the result of a stop request implies STOPPING -> STOPPED
            self._killing = False
            self._delay = 0
            self._exitstatus = Rc(es)

            fmt, args = 'stopped: %s (%s)', (self.name, msg)
            self._check_in_state(ProcessState.STOPPING)
            self._change_state(ProcessState.STOPPED)
            if exit_expected:
                log.info(fmt, *args)
            else:
                log.warning(fmt, *args)

        elif too_quickly:
            # the program did not stay up long enough to make it to RUNNING implies STARTING -> BACKOFF
            self._exitstatus = None
            self._spawn_err = 'Exited too quickly (process log may have details)'
            self._check_in_state(ProcessState.STARTING)
            self._change_state(ProcessState.BACKOFF)
            log.warning('exited: %s (%s)', self.name, msg + '; not expected')

        else:
            # this finish was not the result of a stop request, the program was in the RUNNING state but exited implies
            # RUNNING -> EXITED normally but see next comment
            self._delay = 0
            self._backoff = 0
            self._exitstatus = es

            # if the process was STARTING but a system time change causes self.last_start to be in the future, the
            # normal STARTING->RUNNING transition can be subverted so we perform the transition here.
            if self._state == ProcessState.STARTING:
                self._change_state(ProcessState.RUNNING)

            self._check_in_state(ProcessState.RUNNING)

            if exit_expected:
                # expected exit code
                self._change_state(ProcessState.EXITED, expected=True)
                log.info('exited: %s (%s)', self.name, msg + '; expected')
            else:
                # unexpected exit code
                self._spawn_err = f'Bad exit code {es}'
                self._change_state(ProcessState.EXITED, expected=False)
                log.warning('exited: %s (%s)', self.name, msg + '; not expected')

        self._pid = Pid(0)
        close_parent_pipes(self._pipes)
        self._pipes = ProcessPipes()
        self._dispatchers = Dispatchers([])

    def transition(self) -> None:
        now = time.time()
        state = self._state

        self._check_and_adjust_for_system_clock_rollback(now)

        if self._supervisor_states.state > SupervisorState.RESTARTING:
            # dont start any processes if supervisor is shutting down
            if state == ProcessState.EXITED:
                if self._config.auto_restart:
                    if self._config.auto_restart is RestartUnconditionally:
                        # EXITED -> STARTING
                        self._spawn()
                    elif self._exitstatus not in self._config.exitcodes:
                        # EXITED -> STARTING
                        self._spawn()

            elif state == ProcessState.STOPPED and not self._last_start:
                if self._config.auto_start:
                    # STOPPED -> STARTING
                    self._spawn()

            elif state == ProcessState.BACKOFF:
                if self._backoff <= self._config.start_retries:
                    if now > self._delay:
                        # BACKOFF -> STARTING
                        self._spawn()

        if state == ProcessState.STARTING:
            if now - self._last_start > self._config.start_secs:
                # STARTING -> RUNNING if the proc has started successfully and it has stayed up for at least
                # proc.config.start_secs,
                self._delay = 0
                self._backoff = 0
                self._check_in_state(ProcessState.STARTING)
                self._change_state(ProcessState.RUNNING)
                msg = ('entered RUNNING state, process has stayed up for > than %s seconds (start_secs)' % self._config.start_secs)  # noqa
                log.info('success: %s %s', self.name, msg)

        if state == ProcessState.BACKOFF:
            if self._backoff > self._config.start_retries:
                # BACKOFF -> FATAL if the proc has exceeded its number of retries
                self.give_up()
                msg = ('entered FATAL state, too many start retries too quickly')
                log.info('gave up: %s %s', self.name, msg)

        elif state == ProcessState.STOPPING:
            time_left = self._delay - now
            if time_left <= 0:
                # kill processes which are taking too long to stop with a final sigkill. if this doesn't kill it, the
                # process will be stuck in the STOPPING state forever.
                log.warning('killing \'%s\' (%s) with SIGKILL', self.name, self.pid)
                self.kill(signal.SIGKILL)

    def after_setuid(self) -> None:
        # temporary logfiles which are erased at start time
        # get_autoname = self.context.get_auto_child_log_name  # noqa
        # sid = self.context.config.identifier  # noqa
        # name = self._config.name  # noqa
        # if self.stdout_logfile is Automatic:
        #     self.stdout_logfile = get_autoname(name, sid, 'stdout')
        # if self.stderr_logfile is Automatic:
        #     self.stderr_logfile = get_autoname(name, sid, 'stderr')
        pass
