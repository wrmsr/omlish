# ruff: noqa: UP006 UP007
import dataclasses as dc
import errno
import functools
import os.path
import shlex
import signal
import time
import traceback
import typing as ta

from omlish.lite.check import check_isinstance
from omlish.lite.logs import log

from .compat import as_bytes
from .compat import as_string
from .compat import close_fd
from .compat import compact_traceback
from .compat import decode_wait_status
from .compat import get_path
from .compat import real_exit
from .compat import signame
from .configs import ProcessConfig
from .configs import ProcessGroupConfig
from .context import ServerContext
from .context import check_execv_args
from .context import close_child_pipes
from .context import close_parent_pipes
from .context import drop_privileges
from .context import make_pipes
from .datatypes import RestartUnconditionally
from .dispatchers import Dispatcher
from .dispatchers import InputDispatcher
from .dispatchers import OutputDispatcher
from .events import EVENT_CALLBACKS
from .events import ProcessCommunicationEvent
from .events import ProcessCommunicationStderrEvent
from .events import ProcessCommunicationStdoutEvent
from .events import ProcessStateBackoffEvent
from .events import ProcessStateEvent
from .events import ProcessStateExitedEvent
from .events import ProcessStateFatalEvent
from .events import ProcessStateRunningEvent
from .events import ProcessStateStartingEvent
from .events import ProcessStateStoppedEvent
from .events import ProcessStateStoppingEvent
from .events import ProcessStateUnknownEvent
from .exceptions import BadCommandError
from .exceptions import ProcessError
from .states import STOPPED_STATES
from .states import ProcessState
from .states import SupervisorState
from .types import AbstractServerContext
from .types import AbstractSubprocess


InheritedFds = ta.NewType('InheritedFds', ta.FrozenSet[int])


##


@functools.total_ordering
class Subprocess(AbstractSubprocess):
    """A class to manage a subprocess."""

    def __init__(
            self,
            config: ProcessConfig,
            group: 'ProcessGroup',
            context: AbstractServerContext,
            *,
            inherited_fds: ta.Optional[InheritedFds] = None,
    ) -> None:
        super().__init__()
        self._config = config
        self._group = group
        self._context = context
        self._inherited_fds = InheritedFds(frozenset(inherited_fds or []))

        self._dispatchers: ta.Dict[int, Dispatcher] = {}
        self._pipes: ta.Dict[str, int] = {}

        self._state = ProcessState.STOPPED
        self._pid = 0  # 0 when not running

        self._laststart = 0.  # Last time the subprocess was started; 0 if never
        self._laststop = 0.  # Last time the subprocess was stopped; 0 if never
        self._last_stop_report = 0.  # Last time "waiting for x to stop" logged, to throttle
        self._delay = 0.  # If nonzero, delay starting or killing until this time

        self._administrative_stop = False  # true if process has been stopped by an admin
        self._system_stop = False  # true if process has been stopped by the system

        self._killing = False  # true if we are trying to kill this process

        self._backoff = 0  # backoff counter (to startretries)

        self._exitstatus: ta.Optional[int] = None  # status attached to dead process by finish()
        self._spawn_err: ta.Optional[str] = None  # error message attached by spawn() if any

    @property
    def pid(self) -> int:
        return self._pid

    @property
    def group(self) -> 'ProcessGroup':
        return self._group

    @property
    def config(self) -> ProcessConfig:
        return self._config

    @property
    def context(self) -> AbstractServerContext:
        return self._context

    @property
    def state(self) -> ProcessState:
        return self._state

    @property
    def backoff(self) -> int:
        return self._backoff

    def remove_logs(self) -> None:
        for dispatcher in self._dispatchers.values():
            if hasattr(dispatcher, 'remove_logs'):
                dispatcher.remove_logs()

    def reopen_logs(self) -> None:
        for dispatcher in self._dispatchers.values():
            if hasattr(dispatcher, 'reopen_logs'):
                dispatcher.reopen_logs()

    def drain(self) -> None:
        for dispatcher in self._dispatchers.values():
            # note that we *must* call readable() for every dispatcher, as it may have side effects for a given
            # dispatcher (eg. call handle_listener_state_change for event listener processes)
            if dispatcher.readable():
                dispatcher.handle_read_event()
            if dispatcher.writable():
                dispatcher.handle_write_event()

    def write(self, chars: ta.Union[bytes, str]) -> None:
        if not self.pid or self._killing:
            raise OSError(errno.EPIPE, 'Process already closed')

        stdin_fd = self._pipes['stdin']
        if stdin_fd is None:
            raise OSError(errno.EPIPE, 'Process has no stdin channel')

        dispatcher = check_isinstance(self._dispatchers[stdin_fd], InputDispatcher)
        if dispatcher.closed:
            raise OSError(errno.EPIPE, "Process' stdin channel is closed")

        dispatcher.write(chars)
        dispatcher.flush()  # this must raise EPIPE if the pipe is closed

    def _get_execv_args(self) -> ta.Tuple[str, ta.Sequence[str]]:
        """
        Internal: turn a program name into a file name, using $PATH, make sure it exists / is executable, raising a
        ProcessError if not
        """

        try:
            commandargs = shlex.split(self._config.command)
        except ValueError as e:
            raise BadCommandError(f"can't parse command {self._config.command!r}: {e}")  # noqa

        if commandargs:
            program = commandargs[0]
        else:
            raise BadCommandError('command is empty')

        if '/' in program:
            filename = program
            try:
                st = os.stat(filename)
            except OSError:
                st = None

        else:
            path = get_path()
            found = None
            st = None
            for dir in path:  # noqa
                found = os.path.join(dir, program)
                try:
                    st = os.stat(found)
                except OSError:
                    pass
                else:
                    break
            if st is None:
                filename = program
            else:
                filename = found  # type: ignore

        # check_execv_args will raise a ProcessError if the execv args are bogus, we break it out into a separate
        # options method call here only to service unit tests
        check_execv_args(filename, commandargs, st)

        return filename, commandargs

    event_map: ta.ClassVar[ta.Mapping[ProcessState, ta.Type[ProcessStateEvent]]] = {
        ProcessState.BACKOFF: ProcessStateBackoffEvent,
        ProcessState.FATAL: ProcessStateFatalEvent,
        ProcessState.UNKNOWN: ProcessStateUnknownEvent,
        ProcessState.STOPPED: ProcessStateStoppedEvent,
        ProcessState.EXITED: ProcessStateExitedEvent,
        ProcessState.RUNNING: ProcessStateRunningEvent,
        ProcessState.STARTING: ProcessStateStartingEvent,
        ProcessState.STOPPING: ProcessStateStoppingEvent,
    }

    def change_state(self, new_state: ProcessState, expected: bool = True) -> bool:
        old_state = self._state
        if new_state is old_state:
            return False

        self._state = new_state
        if new_state == ProcessState.BACKOFF:
            now = time.time()
            self._backoff += 1
            self._delay = now + self._backoff

        event_class = self.event_map.get(new_state)
        if event_class is not None:
            event = event_class(self, old_state, expected)
            EVENT_CALLBACKS.notify(event)

        return True

    def _check_in_state(self, *states: ProcessState) -> None:
        if self._state not in states:
            current_state = self._state.name
            allowable_states = ' '.join(s.name for s in states)
            processname = as_string(self._config.name)
            raise AssertionError('Assertion failed for %s: %s not in %s' % (processname, current_state, allowable_states))  # noqa

    def _record_spawn_err(self, msg: str) -> None:
        self._spawn_err = msg
        log.info('_spawn_err: %s', msg)

    def spawn(self) -> ta.Optional[int]:
        processname = as_string(self._config.name)

        if self.pid:
            log.warning('process \'%s\' already running', processname)
            return None

        self._killing = False
        self._spawn_err = None
        self._exitstatus = None
        self._system_stop = False
        self._administrative_stop = False

        self._laststart = time.time()

        self._check_in_state(
            ProcessState.EXITED,
            ProcessState.FATAL,
            ProcessState.BACKOFF,
            ProcessState.STOPPED,
        )

        self.change_state(ProcessState.STARTING)

        try:
            filename, argv = self._get_execv_args()
        except ProcessError as what:
            self._record_spawn_err(what.args[0])
            self._check_in_state(ProcessState.STARTING)
            self.change_state(ProcessState.BACKOFF)
            return None

        try:
            self._dispatchers, self._pipes = self._make_dispatchers()  # type: ignore
        except OSError as why:
            code = why.args[0]
            if code == errno.EMFILE:
                # too many file descriptors open
                msg = f"too many open files to spawn '{processname}'"
            else:
                msg = f"unknown error making dispatchers for '{processname}': {errno.errorcode.get(code, code)}"
            self._record_spawn_err(msg)
            self._check_in_state(ProcessState.STARTING)
            self.change_state(ProcessState.BACKOFF)
            return None

        try:
            pid = os.fork()
        except OSError as why:
            code = why.args[0]
            if code == errno.EAGAIN:
                # process table full
                msg = f'Too many processes in process table to spawn \'{processname}\''
            else:
                msg = f'unknown error during fork for \'{processname}\': {errno.errorcode.get(code, code)}'
            self._record_spawn_err(msg)
            self._check_in_state(ProcessState.STARTING)
            self.change_state(ProcessState.BACKOFF)
            close_parent_pipes(self._pipes)
            close_child_pipes(self._pipes)
            return None

        if pid != 0:
            return self._spawn_as_parent(pid)

        else:
            self._spawn_as_child(filename, argv)
            return None

    def _make_dispatchers(self) -> ta.Tuple[ta.Mapping[int, Dispatcher], ta.Mapping[str, int]]:
        use_stderr = not self._config.redirect_stderr
        p = make_pipes(use_stderr)
        stdout_fd, stderr_fd, stdin_fd = p['stdout'], p['stderr'], p['stdin']
        dispatchers: ta.Dict[int, Dispatcher] = {}
        etype: ta.Type[ProcessCommunicationEvent]
        if stdout_fd is not None:
            etype = ProcessCommunicationStdoutEvent
            dispatchers[stdout_fd] = OutputDispatcher(self, etype, stdout_fd)
        if stderr_fd is not None:
            etype = ProcessCommunicationStderrEvent
            dispatchers[stderr_fd] = OutputDispatcher(self, etype, stderr_fd)
        if stdin_fd is not None:
            dispatchers[stdin_fd] = InputDispatcher(self, 'stdin', stdin_fd)
        return dispatchers, p

    def _spawn_as_parent(self, pid: int) -> int:
        # Parent
        self._pid = pid
        close_child_pipes(self._pipes)
        log.info('spawned: \'%s\' with pid %s', as_string(self._config.name), pid)
        self._spawn_err = None
        self._delay = time.time() + self._config.startsecs
        self.context.pid_history[pid] = self
        return pid

    def _prepare_child_fds(self) -> None:
        os.dup2(self._pipes['child_stdin'], 0)
        os.dup2(self._pipes['child_stdout'], 1)
        if self._config.redirect_stderr:
            os.dup2(self._pipes['child_stdout'], 2)
        else:
            os.dup2(self._pipes['child_stderr'], 2)

        for i in range(3, self.context.config.minfds):
            if i in self._inherited_fds:
                continue
            close_fd(i)

    def _spawn_as_child(self, filename: str, argv: ta.Sequence[str]) -> None:
        try:
            # prevent child from receiving signals sent to the parent by calling os.setpgrp to create a new process
            # group for the child; this prevents, for instance, the case of child processes being sent a SIGINT when
            # running supervisor in foreground mode and Ctrl-C in the terminal window running supervisord is pressed.
            # Presumably it also prevents HUP, etc received by supervisord from being sent to children.
            os.setpgrp()

            self._prepare_child_fds()
            # sending to fd 2 will put this output in the stderr log

            # set user
            setuid_msg = self.set_uid()
            if setuid_msg:
                uid = self._config.uid
                msg = f"couldn't setuid to {uid}: {setuid_msg}\n"
                os.write(2, as_bytes('supervisor: ' + msg))
                return  # finally clause will exit the child process

            # set environment
            env = os.environ.copy()
            env['SUPERVISOR_ENABLED'] = '1'
            env['SUPERVISOR_PROCESS_NAME'] = self._config.name
            if self._group:
                env['SUPERVISOR_GROUP_NAME'] = self._group.config.name
            if self._config.environment is not None:
                env.update(self._config.environment)

            # change directory
            cwd = self._config.directory
            try:
                if cwd is not None:
                    os.chdir(os.path.expanduser(cwd))
            except OSError as why:
                code = errno.errorcode.get(why.args[0], why.args[0])
                msg = f"couldn't chdir to {cwd}: {code}\n"
                os.write(2, as_bytes('supervisor: ' + msg))
                return  # finally clause will exit the child process

            # set umask, then execve
            try:
                if self._config.umask is not None:
                    os.umask(self._config.umask)
                os.execve(filename, list(argv), env)
            except OSError as why:
                code = errno.errorcode.get(why.args[0], why.args[0])
                msg = f"couldn't exec {argv[0]}: {code}\n"
                os.write(2, as_bytes('supervisor: ' + msg))
            except Exception:  # noqa
                (file, fun, line), t, v, tbinfo = compact_traceback()
                error = f'{t}, {v}: file: {file} line: {line}'
                msg = f"couldn't exec {filename}: {error}\n"
                os.write(2, as_bytes('supervisor: ' + msg))

            # this point should only be reached if execve failed. the finally clause will exit the child process.

        finally:
            os.write(2, as_bytes('supervisor: child process was not spawned\n'))
            real_exit(127)  # exit process with code for spawn failure

    def _check_and_adjust_for_system_clock_rollback(self, test_time):
        """
        Check if system clock has rolled backward beyond test_time. If so, set affected timestamps to test_time.
        """
        if self._state == ProcessState.STARTING:
            self._laststart = min(test_time, self._laststart)
            if self._delay > 0 and test_time < (self._delay - self._config.startsecs):
                self._delay = test_time + self._config.startsecs

        elif self._state == ProcessState.RUNNING:
            if test_time > self._laststart and test_time < (self._laststart + self._config.startsecs):
                self._laststart = test_time - self._config.startsecs

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
        self._check_in_state(ProcessState.BACKOFF)
        self.change_state(ProcessState.FATAL)

    def kill(self, sig: int) -> ta.Optional[str]:
        """
        Send a signal to the subprocess with the intention to kill it (to make it exit).  This may or may not actually
        kill it.

        Return None if the signal was sent, or an error message string if an error occurred or if the subprocess is not
        running.
        """
        now = time.time()

        processname = as_string(self._config.name)
        # If the process is in BACKOFF and we want to stop or kill it, then BACKOFF -> STOPPED.  This is needed because
        # if startretries is a large number and the process isn't starting successfully, the stop request would be
        # blocked for a long time waiting for the retries.
        if self._state == ProcessState.BACKOFF:
            log.debug('Attempted to kill %s, which is in BACKOFF state.', processname)
            self.change_state(ProcessState.STOPPED)
            return None

        args: tuple
        if not self.pid:
            fmt, args = "attempted to kill %s with sig %s but it wasn't running", (processname, signame(sig))
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

        log.debug('killing %s (pid %s) %swith signal %s', processname, self.pid, as_group, signame(sig))

        # RUNNING/STARTING/STOPPING -> STOPPING
        self._killing = True
        self._delay = now + self._config.stopwaitsecs
        # we will already be in the STOPPING state if we're doing a SIGKILL as a result of overrunning stopwaitsecs
        self._check_in_state(ProcessState.RUNNING, ProcessState.STARTING, ProcessState.STOPPING)
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
                    log.debug('unable to signal %s (pid %s), it probably just exited on its own: %s', processname, self.pid, str(exc))  # noqa
                    # we could change the state here but we intentionally do not.  we will do it during normal SIGCHLD
                    # processing.
                    return None
                raise
        except Exception:  # noqa
            tb = traceback.format_exc()
            fmt, args = 'unknown problem killing %s (%s):%s', (processname, self.pid, tb)
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
        processname = as_string(self._config.name)
        args: tuple
        if not self.pid:
            fmt, args = "attempted to send %s sig %s but it wasn't running", (processname, signame(sig))
            log.debug(fmt, *args)
            return fmt % args

        log.debug('sending %s (pid %s) sig %s', processname, self.pid, signame(sig))

        self._check_in_state(ProcessState.RUNNING, ProcessState.STARTING, ProcessState.STOPPING)

        try:
            try:
                os.kill(self.pid, sig)
            except OSError as exc:
                if exc.errno == errno.ESRCH:
                    log.debug(
                        'unable to signal %s (pid %s), it probably just now exited on its own: %s',
                        processname,
                        self.pid,
                        str(exc),
                    )
                    # we could change the state here but we intentionally do not.  we will do it during normal SIGCHLD
                    # processing.
                    return None
                raise
        except Exception:  # noqa
            tb = traceback.format_exc()
            fmt, args = 'unknown problem sending sig %s (%s):%s', (processname, self.pid, tb)
            log.critical(fmt, *args)
            self.change_state(ProcessState.UNKNOWN)
            return fmt % args

        return None

    def finish(self, sts: int) -> None:
        """The process was reaped and we need to report and manage its state."""

        self.drain()

        es, msg = decode_wait_status(sts)

        now = time.time()

        self._check_and_adjust_for_system_clock_rollback(now)

        self._laststop = now
        processname = as_string(self._config.name)

        if now > self._laststart:
            too_quickly = now - self._laststart < self._config.startsecs
        else:
            too_quickly = False
            log.warning(
                "process '%s' (%s) laststart time is in the future, don't know how long process was running so "
                "assuming it did not exit too quickly",
                processname,
                self.pid,
            )

        exit_expected = es in self._config.exitcodes

        if self._killing:
            # likely the result of a stop request implies STOPPING -> STOPPED
            self._killing = False
            self._delay = 0
            self._exitstatus = es

            fmt, args = 'stopped: %s (%s)', (processname, msg)
            self._check_in_state(ProcessState.STOPPING)
            self.change_state(ProcessState.STOPPED)
            if exit_expected:
                log.info(fmt, *args)
            else:
                log.warning(fmt, *args)

        elif too_quickly:
            # the program did not stay up long enough to make it to RUNNING implies STARTING -> BACKOFF
            self._exitstatus = None
            self._spawn_err = 'Exited too quickly (process log may have details)'
            self._check_in_state(ProcessState.STARTING)
            self.change_state(ProcessState.BACKOFF)
            log.warning('exited: %s (%s)', processname, msg + '; not expected')

        else:
            # this finish was not the result of a stop request, the program was in the RUNNING state but exited implies
            # RUNNING -> EXITED normally but see next comment
            self._delay = 0
            self._backoff = 0
            self._exitstatus = es

            # if the process was STARTING but a system time change causes self.laststart to be in the future, the normal
            # STARTING->RUNNING transition can be subverted so we perform the transition here.
            if self._state == ProcessState.STARTING:
                self.change_state(ProcessState.RUNNING)

            self._check_in_state(ProcessState.RUNNING)

            if exit_expected:
                # expected exit code
                self.change_state(ProcessState.EXITED, expected=True)
                log.info('exited: %s (%s)', processname, msg + '; expected')
            else:
                # unexpected exit code
                self._spawn_err = f'Bad exit code {es}'
                self.change_state(ProcessState.EXITED, expected=False)
                log.warning('exited: %s (%s)', processname, msg + '; not expected')

        self._pid = 0
        close_parent_pipes(self._pipes)
        self._pipes = {}
        self._dispatchers = {}

    def set_uid(self) -> ta.Optional[str]:
        if self._config.uid is None:
            return None
        msg = drop_privileges(self._config.uid)
        return msg

    def __lt__(self, other):
        return self._config.priority < other.config.priority

    def __eq__(self, other):
        return self._config.priority == other.config.priority

    def __repr__(self):
        # repr can't return anything other than a native string, but the name might be unicode - a problem on Python 2.
        name = self._config.name
        return f'<Subprocess at {id(self)} with name {name} in state {self.get_state().name}>'

    def get_state(self) -> ProcessState:
        return self._state

    def transition(self):
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

            elif state == ProcessState.STOPPED and not self._laststart:
                if self._config.autostart:
                    # STOPPED -> STARTING
                    self.spawn()

            elif state == ProcessState.BACKOFF:
                if self._backoff <= self._config.startretries:
                    if now > self._delay:
                        # BACKOFF -> STARTING
                        self.spawn()

        processname = as_string(self._config.name)
        if state == ProcessState.STARTING:
            if now - self._laststart > self._config.startsecs:
                # STARTING -> RUNNING if the proc has started successfully and it has stayed up for at least
                # proc.config.startsecs,
                self._delay = 0
                self._backoff = 0
                self._check_in_state(ProcessState.STARTING)
                self.change_state(ProcessState.RUNNING)
                msg = ('entered RUNNING state, process has stayed up for > than %s seconds (startsecs)' % self._config.startsecs)  # noqa
                logger.info('success: %s %s', processname, msg)

        if state == ProcessState.BACKOFF:
            if self._backoff > self._config.startretries:
                # BACKOFF -> FATAL if the proc has exceeded its number of retries
                self.give_up()
                msg = ('entered FATAL state, too many start retries too quickly')
                logger.info('gave up: %s %s', processname, msg)

        elif state == ProcessState.STOPPING:
            time_left = self._delay - now
            if time_left <= 0:
                # kill processes which are taking too long to stop with a final sigkill.  if this doesn't kill it, the
                # process will be stuck in the STOPPING state forever.
                log.warning('killing \'%s\' (%s) with SIGKILL', processname, self.pid)
                self.kill(signal.SIGKILL)

    def create_auto_child_logs(self):
        # temporary logfiles which are erased at start time
        # get_autoname = self.context.get_auto_child_log_name  # noqa
        # sid = self.context.config.identifier  # noqa
        # name = self._config.name  # noqa
        # if self.stdout_logfile is Automatic:
        #     self.stdout_logfile = get_autoname(name, sid, 'stdout')
        # if self.stderr_logfile is Automatic:
        #     self.stderr_logfile = get_autoname(name, sid, 'stderr')
        pass


##


@dc.dataclass(frozen=True)
class SubprocessFactory:
    fn: ta.Callable[[ProcessConfig, 'ProcessGroup'], Subprocess]

    def __call__(self, config: ProcessConfig, group: 'ProcessGroup') -> Subprocess:
        return self.fn(config, group)


@functools.total_ordering
class ProcessGroup:
    def __init__(
            self,
            config: ProcessGroupConfig,
            context: ServerContext,
            *,
            subprocess_factory: ta.Optional[SubprocessFactory] = None,
    ):
        super().__init__()
        self._config = config
        self._context = context

        if subprocess_factory is None:
            def make_subprocess(config: ProcessConfig, group: ProcessGroup) -> Subprocess:
                return Subprocess(config, group, self._context)
            subprocess_factory = SubprocessFactory(make_subprocess)
        self._subprocess_factory = subprocess_factory

        self._processes = {}
        for pconfig in self._config.processes or []:
            process = self._subprocess_factory(pconfig, self)
            self._processes[pconfig.name] = process

    @property
    def config(self) -> ProcessGroupConfig:
        return self._config

    @property
    def context(self) -> AbstractServerContext:
        return self._context

    def __lt__(self, other):
        return self._config.priority < other.config.priority

    def __eq__(self, other):
        return self._config.priority == other.config.priority

    def __repr__(self):
        # repr can't return anything other than a native string, but the name might be unicode - a problem on Python 2.
        name = self._config.name
        return f'<{self.__class__.__name__} instance at {id(self)} named {name}>'

    def remove_logs(self) -> None:
        for process in self._processes.values():
            process.remove_logs()

    def reopen_logs(self) -> None:
        for process in self._processes.values():
            process.reopen_logs()

    def stop_all(self) -> None:
        processes = list(self._processes.values())
        processes.sort()
        processes.reverse()  # stop in desc priority order

        for proc in processes:
            state = proc.get_state()
            if state == ProcessState.RUNNING:
                # RUNNING -> STOPPING
                proc.stop()

            elif state == ProcessState.STARTING:
                # STARTING -> STOPPING
                proc.stop()

            elif state == ProcessState.BACKOFF:
                # BACKOFF -> FATAL
                proc.give_up()

    def get_unstopped_processes(self) -> ta.List[Subprocess]:
        return [x for x in self._processes.values() if x.get_state() not in STOPPED_STATES]

    def get_dispatchers(self) -> ta.Dict[int, Dispatcher]:
        dispatchers = {}
        for process in self._processes.values():
            dispatchers.update(process._dispatchers)  # noqa
        return dispatchers

    def before_remove(self) -> None:
        pass

    def transition(self) -> None:
        for proc in self._processes.values():
            proc.transition()

    def after_setuid(self) -> None:
        for proc in self._processes.values():
            proc.create_auto_child_logs()
