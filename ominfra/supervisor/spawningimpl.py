# ruff: noqa: UP006 UP007
import errno
import os.path
import shlex
import stat
import typing as ta

from omlish.io.fdio.handlers import FdioHandler
from omlish.lite.check import check
from omlish.lite.typing import Func3

from .configs import ProcessConfig
from .configs import ServerConfig
from .dispatchers import Dispatchers
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
from .pipes import close_pipes
from .pipes import make_process_pipes
from .privileges import drop_privileges
from .process import PidHistory
from .spawning import ProcessSpawnError
from .spawning import ProcessSpawning
from .spawning import SpawnedProcess
from .types import Process
from .types import ProcessGroup
from .types import ProcessInputDispatcher
from .types import ProcessOutputDispatcher
from .utils.diag import compact_traceback
from .utils.fds import close_fd
from .utils.fs import get_path
from .utils.os import real_exit
from .utils.ostypes import Fd
from .utils.ostypes import Pid
from .utils.ostypes import Rc
from .utils.strings import as_bytes


class ProcessOutputDispatcherFactory(Func3[Process, ta.Type[ProcessCommunicationEvent], Fd, ProcessOutputDispatcher]):
    pass


class ProcessInputDispatcherFactory(Func3[Process, str, Fd, ProcessInputDispatcher]):
    pass


InheritedFds = ta.NewType('InheritedFds', ta.FrozenSet[Fd])


##


class ProcessSpawningImpl(ProcessSpawning):
    def __init__(
            self,
            process: Process,
            *,
            server_config: ServerConfig,
            pid_history: PidHistory,

            output_dispatcher_factory: ProcessOutputDispatcherFactory,
            input_dispatcher_factory: ProcessInputDispatcherFactory,

            inherited_fds: ta.Optional[InheritedFds] = None,
    ) -> None:
        super().__init__()

        self._process = process

        self._server_config = server_config
        self._pid_history = pid_history

        self._output_dispatcher_factory = output_dispatcher_factory
        self._input_dispatcher_factory = input_dispatcher_factory

        self._inherited_fds = InheritedFds(frozenset(inherited_fds or []))

    #

    @property
    def process(self) -> Process:
        return self._process

    @property
    def config(self) -> ProcessConfig:
        return self._process.config

    @property
    def group(self) -> ProcessGroup:
        return self._process.group

    #

    def spawn(self) -> SpawnedProcess:  # Raises[ProcessSpawnError]
        try:
            exe, argv = self._get_execv_args()
        except ProcessError as exc:
            raise ProcessSpawnError(exc.args[0]) from exc

        try:
            pipes = make_process_pipes(not self.config.redirect_stderr)
        except OSError as exc:
            code = exc.args[0]
            if code == errno.EMFILE:
                # too many file descriptors open
                msg = f"Too many open files to spawn '{self.process.name}'"
            else:
                msg = f"Unknown error making pipes for '{self.process.name}': {errno.errorcode.get(code, code)}"
            raise ProcessSpawnError(msg) from exc

        try:
            dispatchers = self._make_dispatchers(pipes)
        except Exception as exc:  # noqa
            close_pipes(pipes)
            raise ProcessSpawnError(f"Unknown error making dispatchers for '{self.process.name}': {exc}") from exc

        try:
            pid = Pid(os.fork())
        except OSError as exc:
            code = exc.args[0]
            if code == errno.EAGAIN:
                # process table full
                msg = f"Too many processes in process table to spawn '{self.process.name}'"
            else:
                msg = f"Unknown error during fork for '{self.process.name}': {errno.errorcode.get(code, code)}"
            err = ProcessSpawnError(msg)
            close_pipes(pipes)
            raise err from exc

        if pid != 0:
            sp = SpawnedProcess(
                pid,
                pipes,
                dispatchers,
            )
            self._spawn_as_parent(sp)
            return sp

        else:
            self._spawn_as_child(
                exe,
                argv,
                pipes,
            )
            raise RuntimeError('Unreachable')  # noqa

    def _get_execv_args(self) -> ta.Tuple[str, ta.Sequence[str]]:
        """
        Internal: turn a program name into a file name, using $PATH, make sure it exists / is executable, raising a
        ProcessError if not
        """

        try:
            args = shlex.split(self.config.command)
        except ValueError as e:
            raise BadCommandError(f"Can't parse command {self.config.command!r}: {e}")  # noqa

        if args:
            program = args[0]
        else:
            raise BadCommandError('Command is empty')

        if '/' in program:
            exe = program
            try:
                st = os.stat(exe)
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
                exe = program
            else:
                exe = found  # type: ignore

        # check_execv_args will raise a ProcessError if the execv args are bogus, we break it out into a separate
        # options method call here only to service unit tests
        check_execv_args(exe, args, st)

        return exe, args

    def _make_dispatchers(self, pipes: ProcessPipes) -> Dispatchers:
        dispatchers: ta.List[FdioHandler] = []

        if pipes.stdout is not None:
            dispatchers.append(check.isinstance(self._output_dispatcher_factory(
                self.process,
                ProcessCommunicationStdoutEvent,
                pipes.stdout,
            ), ProcessOutputDispatcher))

        if pipes.stderr is not None:
            dispatchers.append(check.isinstance(self._output_dispatcher_factory(
                self.process,
                ProcessCommunicationStderrEvent,
                pipes.stderr,
            ), ProcessOutputDispatcher))

        if pipes.stdin is not None:
            dispatchers.append(check.isinstance(self._input_dispatcher_factory(
                self.process,
                'stdin',
                pipes.stdin,
            ), ProcessInputDispatcher))

        return Dispatchers(dispatchers)

    #

    def _spawn_as_parent(self, sp: SpawnedProcess) -> None:
        close_child_pipes(sp.pipes)

        self._pid_history[sp.pid] = self.process

    #

    def _spawn_as_child(
            self,
            exe: str,
            argv: ta.Sequence[str],
            pipes: ProcessPipes,
    ) -> ta.NoReturn:
        try:
            # Prevent child from receiving signals sent to the parent by calling os.setpgrp to create a new process
            # group for the child. This prevents, for instance, the case of child processes being sent a SIGINT when
            # running supervisor in foreground mode and Ctrl-C in the terminal window running supervisord is pressed.
            # Presumably it also prevents HUP, etc. received by supervisord from being sent to children.
            os.setpgrp()

            #

            # After preparation sending to fd 2 will put this output in the stderr log.
            self._prepare_child_fds(pipes)

            #

            setuid_msg = self._set_uid()
            if setuid_msg:
                uid = self.config.uid
                msg = f"Couldn't setuid to {uid}: {setuid_msg}\n"
                os.write(2, as_bytes('supervisor: ' + msg))
                raise RuntimeError(msg)

            #

            env = os.environ.copy()
            env['SUPERVISOR_ENABLED'] = '1'
            env['SUPERVISOR_PROCESS_NAME'] = self.process.name
            if self.group:
                env['SUPERVISOR_GROUP_NAME'] = self.group.name
            if self.config.environment is not None:
                env.update(self.config.environment)

            #

            cwd = self.config.directory
            try:
                if cwd is not None:
                    os.chdir(os.path.expanduser(cwd))
            except OSError as exc:
                code = errno.errorcode.get(exc.args[0], exc.args[0])
                msg = f"Couldn't chdir to {cwd}: {code}\n"
                os.write(2, as_bytes('supervisor: ' + msg))
                raise RuntimeError(msg) from exc

            #

            try:
                if self.config.umask is not None:
                    os.umask(self.config.umask)
                os.execve(exe, list(argv), env)

            except OSError as exc:
                code = errno.errorcode.get(exc.args[0], exc.args[0])
                msg = f"Couldn't exec {argv[0]}: {code}\n"
                os.write(2, as_bytes('supervisor: ' + msg))

            except Exception:  # noqa
                (file, fun, line), t, v, tb = compact_traceback()
                msg = f"Couldn't exec {exe}: {t}, {v}: file: {file} line: {line}\n"
                os.write(2, as_bytes('supervisor: ' + msg))

        finally:
            os.write(2, as_bytes('supervisor: child process was not spawned\n'))
            real_exit(Rc(127))  # exit process with code for spawn failure

        raise RuntimeError('Unreachable')

    def _prepare_child_fds(self, pipes: ProcessPipes) -> None:
        os.dup2(check.not_none(pipes.child_stdin), 0)

        os.dup2(check.not_none(pipes.child_stdout), 1)

        if self.config.redirect_stderr:
            os.dup2(check.not_none(pipes.child_stdout), 2)
        else:
            os.dup2(check.not_none(pipes.child_stderr), 2)

        for i in range(3, self._server_config.min_fds):
            if i in self._inherited_fds:
                continue
            close_fd(Fd(i))

    def _set_uid(self) -> ta.Optional[str]:
        if self.config.uid is None:
            return None

        msg = drop_privileges(self.config.uid)
        return msg


##


def check_execv_args(
        exe: str,
        argv: ta.Sequence[str],
        st: ta.Optional[os.stat_result],
) -> None:
    if st is None:
        raise NotFoundError(f"Can't find command {exe!r}")

    elif stat.S_ISDIR(st[stat.ST_MODE]):
        raise NotExecutableError(f'Command at {exe!r} is a directory')

    elif not (stat.S_IMODE(st[stat.ST_MODE]) & 0o111):
        raise NotExecutableError(f'Command at {exe!r} is not executable')

    elif not os.access(exe, os.X_OK):
        raise NoPermissionError(f'No permission to run command {exe!r}')
