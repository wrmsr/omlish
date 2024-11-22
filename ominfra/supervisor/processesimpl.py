# ruff: noqa: UP006 UP007
import errno
import os.path
import shlex
import signal
import stat
import time
import traceback
import typing as ta

from omlish.lite.check import check_isinstance
from omlish.lite.check import check_not_none
from omlish.lite.logs import log
from omlish.lite.typing import Func1

from .spawning import ProcessSpawning
from .spawning import SpawnedProcess
from .spawning import ProcessSpawnError
from .configs import ProcessConfig
from .context import drop_privileges
from .datatypes import RestartUnconditionally
from .dispatchers import Dispatchers
from .events import PROCESS_STATE_EVENT_MAP
from .events import EventCallbacks
from .events import ProcessCommunicationEvent
from .events import ProcessCommunicationStderrEvent
from .events import ProcessCommunicationStdoutEvent
from .exceptions import BadCommandError
from .exceptions import NoPermissionError
from .exceptions import NotExecutableError
from .exceptions import NotFoundError
from .exceptions import ProcessError
from .pipes import ProcessPipes
from .pipes import close_child_pipes
from .pipes import close_parent_pipes
from .pipes import make_process_pipes
from .signals import sig_name
from .states import ProcessState
from .states import SupervisorState
from .types import Dispatcher
from .types import InputDispatcher
from .types import OutputDispatcher
from .types import Process
from .types import ProcessGroup
from .types import ServerContext
from .utils import as_bytes
from .utils import as_string
from .utils import close_fd
from .utils import compact_traceback
from .utils import decode_wait_status
from .utils import get_path
from .utils import real_exit
from .processes import ProcessStateError
from .spawning import ProcessSpawning
from .spawning import ProcessSpawnError


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
            context: ServerContext,
            event_callbacks: EventCallbacks,
            process_spawning_factory: ProcessSpawningFactory,
    ) -> None:
        super().__init__()

        self._config = config
        self._group = group

        self._context = context
        self._event_callbacks = event_callbacks
        self._process_spawning_factory = process_spawning_factory

        #

        self._dispatchers = Dispatchers([])
        self._pipes = ProcessPipes()

        self._state = ProcessState.STOPPED
        self._pid = 0  # 0 when not running

        self._last_start = 0.  # Last time the subprocess was started; 0 if never
        self._last_stop = 0.  # Last time the subprocess was stopped; 0 if never
        self._last_stop_report = 0.  # Last time "waiting for x to stop" logged, to throttle
        self._delay = 0.  # If nonzero, delay starting or killing until this time

        self._administrative_stop = False  # true if process has been stopped by an admin
        self._system_stop = False  # true if process has been stopped by the system

        self._killing = False  # true if we are trying to kill this process

        self._backoff = 0  # backoff counter (to startretries)

        self._exitstatus: ta.Optional[int] = None  # status attached to dead process by finish()
        self._spawn_err: ta.Optional[str] = None  # error message attached by spawn() if any

    #

    def __repr__(self) -> str:
        return f'<Subprocess at {id(self)} with name {self._config.name} in state {self.get_state().name}>'

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
    def pid(self) -> int:
        return self._pid

    #

    @property
    def context(self) -> ServerContext:
        return self._context

    @property
    def state(self) -> ProcessState:
        return self._state

    @property
    def backoff(self) -> int:
        return self._backoff

    #

    def spawn_OLD_STUFF(self) -> ta.Optional[int]:
        process_name = as_string(self._config.name)

        if self.pid:
            log.warning('process \'%s\' already running', process_name)
            return None

        self.check_in_state(
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

        self.change_state(ProcessState.STARTING)

        res = self._spawning.spawn()

        if err:
            self.check_in_state(ProcessState.STARTING)
            self.change_state(ProcessState.BACKOFF)

        else:
            log.info('spawned: \'%s\' with pid %s', as_string(self.name), pid)

            self._pid = pid
            self._delay = time.time() + self.config.startsecs

            return pid

    def get_dispatchers(self) -> Dispatchers:
        return self._dispatchers

    def write(self, chars: ta.Union[bytes, str]) -> None:
        if not self.pid or self._killing:
            raise OSError(errno.EPIPE, 'Process already closed')

        stdin_fd = self._pipes.stdin
        if stdin_fd is None:
            raise OSError(errno.EPIPE, 'Process has no stdin channel')

        dispatcher = check_isinstance(self._dispatchers[stdin_fd], InputDispatcher)
        if dispatcher.closed:
            raise OSError(errno.EPIPE, "Process' stdin channel is closed")

        dispatcher.write(chars)
        dispatcher.flush()  # this must raise EPIPE if the pipe is closed

    #

    def change_state(self, new_state: ProcessState, expected: bool = True) -> bool:
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

    def check_in_state(self, *states: ProcessState) -> None:
        if self._state not in states:
            raise ProcessStateError(
                f'Check failed for {self._config.name}: '
                f'{self._state.name} not in {" ".join(s.name for s in states)}'
            )

    #

    def _check_and_adjust_for_system_clock_rollback(self, test_time):
        """
        Check if system clock has rolled backward beyond test_time. If so, set affected timestamps to test_time.
        """

        if self._state == ProcessState.STARTING:
            self._last_start = min(test_time, self._last_start)
            if self._delay > 0 and test_time < (self._delay - self._config.startsecs):
                self._delay = test_time + self._config.startsecs

        elif self._state == ProcessState.RUNNING:
            if test_time > self._last_start and test_time < (self._last_start + self._config.startsecs):
                self._last_start = test_time - self._config.startsecs

        elif self._state == ProcessState.STOPPING:
            self._last_stop_report = min(test_time, self._last_stop_report)
            if self._delay > 0 and test_time < (self._delay - self._config.stopwaitsecs):
                self._delay = test_time + self._config.stopwaitsecs

        elif self._state == ProcessState.BACKOFF:
            if self._delay > 0 and test_time < (self._delay - self._backoff):
                self._delay = test_time + self._backoff

    def stop(self) -> ta.Optional[str]:
        self._administrative_stop = True
        self._last_stop_report = 0
        return self.kill(self._config.stopsignal)

    def stop_report(self) -> None:
        """Log a 'waiting for x to stop' message with throttling."""

        if self._state == ProcessState.STOPPING:
            now = time.time()

            self._check_and_adjust_for_system_clock_rollback(now)

            if now > (self._last_stop_report + 2):  # every 2 seconds
                log.info('waiting for %s to stop', as_string(self._config.name))
                self._last_stop_report = now

    def give_up(self) -> None:
        self._delay = 0
        self._backoff = 0
        self._system_stop = True
        self.check_in_state(ProcessState.BACKOFF)
        self.change_state(ProcessState.FATAL)

    def kill(self, sig: int) -> ta.Optional[str]:
        """
        Send a signal to the subprocess with the intention to kill it (to make it exit).  This may or may not actually
        kill it.

        Return None if the signal was sent, or an error message string if an error occurred or if the subprocess is not
        running.
        """
        now = time.time()

        process_name = as_string(self._config.name)
        # If the process is in BACKOFF and we want to stop or kill it, then BACKOFF -> STOPPED.  This is needed because
        # if startretries is a large number and the process isn't starting successfully, the stop request would be
        # blocked for a long time waiting for the retries.
        if self._state == ProcessState.BACKOFF:
            log.debug('Attempted to kill %s, which is in BACKOFF state.', process_name)
            self.change_state(ProcessState.STOPPED)
            return None

        args: tuple
        if not self.pid:
            fmt, args = "attempted to kill %s with sig %s but it wasn't running", (process_name, sig_name(sig))
            log.debug(fmt, *args)
            return fmt % args

        # If we're in the stopping state, then we've already sent the stop signal and this is the kill signal
        if self._state == ProcessState.STOPPING:
            killasgroup = self._config.killasgroup
        else:
            killasgroup = self._config.stopasgroup

        as_group = ''
        if killasgroup:
            as_group = 'process group '

        log.debug('killing %s (pid %s) %s with signal %s', process_name, self.pid, as_group, sig_name(sig))

        # RUNNING/STARTING/STOPPING -> STOPPING
        self._killing = True
        self._delay = now + self._config.stopwaitsecs
        # we will already be in the STOPPING state if we're doing a SIGKILL as a result of overrunning stopwaitsecs
        self.check_in_state(ProcessState.RUNNING, ProcessState.STARTING, ProcessState.STOPPING)
        self.change_state(ProcessState.STOPPING)

        pid = self.pid
        if killasgroup:
            # send to the whole process group instead
            pid = -self.pid

        try:
            try:
                os.kill(pid, sig)
            except OSError as exc:
                if exc.errno == errno.ESRCH:
                    log.debug('unable to signal %s (pid %s), it probably just exited on its own: %s', process_name, self.pid, str(exc))  # noqa
                    # we could change the state here but we intentionally do not.  we will do it during normal SIGCHLD
                    # processing.
                    return None
                raise
        except Exception:  # noqa
            tb = traceback.format_exc()
            fmt, args = 'unknown problem killing %s (%s):%s', (process_name, self.pid, tb)
            log.critical(fmt, *args)
            self.change_state(ProcessState.UNKNOWN)
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
        process_name = as_string(self._config.name)
        args: tuple
        if not self.pid:
            fmt, args = "attempted to send %s sig %s but it wasn't running", (process_name, sig_name(sig))
            log.debug(fmt, *args)
            return fmt % args

        log.debug('sending %s (pid %s) sig %s', process_name, self.pid, sig_name(sig))

        self.check_in_state(ProcessState.RUNNING, ProcessState.STARTING, ProcessState.STOPPING)

        try:
            try:
                os.kill(self.pid, sig)
            except OSError as exc:
                if exc.errno == errno.ESRCH:
                    log.debug(
                        'unable to signal %s (pid %s), it probably just now exited on its own: %s',
                        process_name,
                        self.pid,
                        str(exc),
                    )
                    # we could change the state here but we intentionally do not.  we will do it during normal SIGCHLD
                    # processing.
                    return None
                raise
        except Exception:  # noqa
            tb = traceback.format_exc()
            fmt, args = 'unknown problem sending sig %s (%s):%s', (process_name, self.pid, tb)
            log.critical(fmt, *args)
            self.change_state(ProcessState.UNKNOWN)
            return fmt % args

        return None

    def finish(self, sts: int) -> None:
        """The process was reaped and we need to report and manage its state."""

        self._dispatchers.drain()

        es, msg = decode_wait_status(sts)

        now = time.time()

        self._check_and_adjust_for_system_clock_rollback(now)

        self._last_stop = now
        process_name = as_string(self._config.name)

        if now > self._last_start:
            too_quickly = now - self._last_start < self._config.startsecs
        else:
            too_quickly = False
            log.warning(
                "process '%s' (%s) last_start time is in the future, don't know how long process was running so "
                "assuming it did not exit too quickly",
                process_name,
                self.pid,
            )

        exit_expected = es in self._config.exitcodes

        if self._killing:
            # likely the result of a stop request implies STOPPING -> STOPPED
            self._killing = False
            self._delay = 0
            self._exitstatus = es

            fmt, args = 'stopped: %s (%s)', (process_name, msg)
            self.check_in_state(ProcessState.STOPPING)
            self.change_state(ProcessState.STOPPED)
            if exit_expected:
                log.info(fmt, *args)
            else:
                log.warning(fmt, *args)

        elif too_quickly:
            # the program did not stay up long enough to make it to RUNNING implies STARTING -> BACKOFF
            self._exitstatus = None
            self._spawn_err = 'Exited too quickly (process log may have details)'
            self.check_in_state(ProcessState.STARTING)
            self.change_state(ProcessState.BACKOFF)
            log.warning('exited: %s (%s)', process_name, msg + '; not expected')

        else:
            # this finish was not the result of a stop request, the program was in the RUNNING state but exited implies
            # RUNNING -> EXITED normally but see next comment
            self._delay = 0
            self._backoff = 0
            self._exitstatus = es

            # if the process was STARTING but a system time change causes self.last_start to be in the future, the
            # normal STARTING->RUNNING transition can be subverted so we perform the transition here.
            if self._state == ProcessState.STARTING:
                self.change_state(ProcessState.RUNNING)

            self.check_in_state(ProcessState.RUNNING)

            if exit_expected:
                # expected exit code
                self.change_state(ProcessState.EXITED, expected=True)
                log.info('exited: %s (%s)', process_name, msg + '; expected')
            else:
                # unexpected exit code
                self._spawn_err = f'Bad exit code {es}'
                self.change_state(ProcessState.EXITED, expected=False)
                log.warning('exited: %s (%s)', process_name, msg + '; not expected')

        self._pid = 0
        close_parent_pipes(self._pipes)
        self._pipes = ProcessPipes()
        self._dispatchers = Dispatchers([])

    def get_state(self) -> ProcessState:
        return self._state

    def transition(self) -> None:
        now = time.time()
        state = self._state

        self._check_and_adjust_for_system_clock_rollback(now)

        logger = log

        if self.context.state > SupervisorState.RESTARTING:
            # dont start any processes if supervisor is shutting down
            if state == ProcessState.EXITED:
                if self._config.autorestart:
                    if self._config.autorestart is RestartUnconditionally:
                        # EXITED -> STARTING
                        self.spawn()
                    elif self._exitstatus not in self._config.exitcodes:
                        # EXITED -> STARTING
                        self.spawn()

            elif state == ProcessState.STOPPED and not self._last_start:
                if self._config.autostart:
                    # STOPPED -> STARTING
                    self.spawn()

            elif state == ProcessState.BACKOFF:
                if self._backoff <= self._config.startretries:
                    if now > self._delay:
                        # BACKOFF -> STARTING
                        self.spawn()

        process_name = as_string(self._config.name)
        if state == ProcessState.STARTING:
            if now - self._last_start > self._config.startsecs:
                # STARTING -> RUNNING if the proc has started successfully and it has stayed up for at least
                # proc.config.startsecs,
                self._delay = 0
                self._backoff = 0
                self.check_in_state(ProcessState.STARTING)
                self.change_state(ProcessState.RUNNING)
                msg = ('entered RUNNING state, process has stayed up for > than %s seconds (startsecs)' % self._config.startsecs)  # noqa
                logger.info('success: %s %s', process_name, msg)

        if state == ProcessState.BACKOFF:
            if self._backoff > self._config.startretries:
                # BACKOFF -> FATAL if the proc has exceeded its number of retries
                self.give_up()
                msg = ('entered FATAL state, too many start retries too quickly')
                logger.info('gave up: %s %s', process_name, msg)

        elif state == ProcessState.STOPPING:
            time_left = self._delay - now
            if time_left <= 0:
                # kill processes which are taking too long to stop with a final sigkill.  if this doesn't kill it, the
                # process will be stuck in the STOPPING state forever.
                log.warning('killing \'%s\' (%s) with SIGKILL', process_name, self.pid)
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
