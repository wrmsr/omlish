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
from omlish.lite.typing import Func3

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


class OutputDispatcherFactory(Func3[Process, ta.Type[ProcessCommunicationEvent], int, OutputDispatcher]):
    pass


class InputDispatcherFactory(Func3[Process, str, int, InputDispatcher]):
    pass


InheritedFds = ta.NewType('InheritedFds', ta.FrozenSet[int])


##


class ProcessSpawning(Process):
    """A class to manage a subprocess."""

    def __init__(
            self,
            config: ProcessConfig,
            group: ProcessGroup,
            *,
            output_dispatcher_factory: OutputDispatcherFactory,
            input_dispatcher_factory: InputDispatcherFactory,

            inherited_fds: ta.Optional[InheritedFds] = None,
    ) -> None:
        super().__init__()

        self._config = config
        self._group = group

        self._output_dispatcher_factory = output_dispatcher_factory
        self._input_dispatcher_factory = input_dispatcher_factory

        self._inherited_fds = InheritedFds(frozenset(inherited_fds or []))

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

    #

    def _record_spawn_err(self, msg: str) -> None:
        self._spawn_err = msg
        log.info('_spawn_err: %s', msg)

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

    def spawn(self) -> ta.Optional[int]:
        process_name = as_string(self._config.name)

        if self.pid:
            log.warning('process \'%s\' already running', process_name)
            return None

        self._killing = False
        self._spawn_err = None
        self._exitstatus = None
        self._system_stop = False
        self._administrative_stop = False

        self._last_start = time.time()

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
            self._dispatchers, self._pipes = self._make_dispatchers()
        except OSError as why:
            code = why.args[0]
            if code == errno.EMFILE:
                # too many file descriptors open
                msg = f"too many open files to spawn '{process_name}'"
            else:
                msg = f"unknown error making dispatchers for '{process_name}': {errno.errorcode.get(code, code)}"
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
                msg = f'Too many processes in process table to spawn \'{process_name}\''
            else:
                msg = f'unknown error during fork for \'{process_name}\': {errno.errorcode.get(code, code)}'
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

    def _make_dispatchers(self) -> ta.Tuple[Dispatchers, ProcessPipes]:
        use_stderr = not self._config.redirect_stderr

        p = make_process_pipes(use_stderr)

        dispatchers: ta.List[Dispatcher] = []

        etype: ta.Type[ProcessCommunicationEvent]
        if p.stdout is not None:
            etype = ProcessCommunicationStdoutEvent
            dispatchers.append(check_isinstance(self._output_dispatcher_factory(
                self,
                etype,
                p.stdout,
            ), OutputDispatcher))

        if p.stderr is not None:
            etype = ProcessCommunicationStderrEvent
            dispatchers.append(check_isinstance(self._output_dispatcher_factory(
                self,
                etype,
                p.stderr,
            ), OutputDispatcher))

        if p.stdin is not None:
            dispatchers.append(check_isinstance(self._input_dispatcher_factory(
                self,
                'stdin',
                p.stdin,
            ), InputDispatcher))

        return Dispatchers(dispatchers), p

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
        os.dup2(check_not_none(self._pipes.child_stdin), 0)
        os.dup2(check_not_none(self._pipes.child_stdout), 1)
        if self._config.redirect_stderr:
            os.dup2(check_not_none(self._pipes.child_stdout), 2)
        else:
            os.dup2(check_not_none(self._pipes.child_stderr), 2)

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


##


def check_execv_args(filename, argv, st) -> None:
    if st is None:
        raise NotFoundError(f"can't find command {filename!r}")

    elif stat.S_ISDIR(st[stat.ST_MODE]):
        raise NotExecutableError(f'command at {filename!r} is a directory')

    elif not (stat.S_IMODE(st[stat.ST_MODE]) & 0o111):
        raise NotExecutableError(f'command at {filename!r} is not executable')

    elif not os.access(filename, os.X_OK):
        raise NoPermissionError(f'no permission to run command {filename!r}')
