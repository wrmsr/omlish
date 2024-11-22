# ruff: noqa: UP006 UP007
import dataclasses as dc
import errno
import os.path
import shlex
import stat
import typing as ta

from omlish.lite.check import check_isinstance
from omlish.lite.check import check_not_none
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
from .pipes import close_pipes
from .pipes import close_child_pipes
from .pipes import make_process_pipes
from .privileges import drop_privileges
from .processes import PidHistory
from .types import Dispatcher
from .types import InputDispatcher
from .types import OutputDispatcher
from .types import Process
from .types import ProcessGroup
from .utils import as_bytes
from .utils import close_fd
from .utils import compact_traceback
from .utils import get_path
from .utils import real_exit


class OutputDispatcherFactory(Func3[Process, ta.Type[ProcessCommunicationEvent], int, OutputDispatcher]):
    pass


class InputDispatcherFactory(Func3[Process, str, int, InputDispatcher]):
    pass


InheritedFds = ta.NewType('InheritedFds', ta.FrozenSet[int])


##


@dc.dataclass(frozen=True)
class SpawnedProcess:
    pid: int
    pipes: ProcessPipes
    dispatchers: Dispatchers


class ProcessSpawnError(RuntimeError):
    pass


class ProcessSpawning:
    """A class to manage a subprocess."""

    def __init__(
            self,
            process: Process,
            *,
            server_config: ServerConfig,
            pid_history: PidHistory,

            output_dispatcher_factory: OutputDispatcherFactory,
            input_dispatcher_factory: InputDispatcherFactory,

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
            raise ProcessSpawnError(f"Unknown error making dispatchers for '{self.process.name}'") from exc

        try:
            pid = os.fork()
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

    def _get_execv_args(self) -> ta.Tuple[str, ta.Sequence[str]]:
        """
        Internal: turn a program name into a file name, using $PATH, make sure it exists / is executable, raising a
        ProcessError if not
        """

        try:
            args = shlex.split(self.config.command)
        except ValueError as e:
            raise BadCommandError(f"can't parse command {self.config.command!r}: {e}")  # noqa

        if args:
            program = args[0]
        else:
            raise BadCommandError('command is empty')

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
        dispatchers: ta.List[Dispatcher] = []

        if pipes.stdout is not None:
            dispatchers.append(check_isinstance(self._output_dispatcher_factory(
                self,
                ProcessCommunicationStdoutEvent,
                pipes.stdout,
            ), OutputDispatcher))

        if pipes.stderr is not None:
            dispatchers.append(check_isinstance(self._output_dispatcher_factory(
                self,
                ProcessCommunicationStderrEvent,
                pipes.stderr,
            ), OutputDispatcher))

        if pipes.stdin is not None:
            dispatchers.append(check_isinstance(self._input_dispatcher_factory(
                self,
                'stdin',
                pipes.stdin,
            ), InputDispatcher))

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
                msg = f"couldn't setuid to {uid}: {setuid_msg}\n"
                os.write(2, as_bytes('supervisor: ' + msg))
                return  # finally clause will exit the child process

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
            except OSError as why:
                code = errno.errorcode.get(why.args[0], why.args[0])
                msg = f"couldn't chdir to {cwd}: {code}\n"
                os.write(2, as_bytes('supervisor: ' + msg))
                return  # finally clause will exit the child process

            #

            try:
                if self.config.umask is not None:
                    os.umask(self.config.umask)
                os.execve(exe, list(argv), env)

            except OSError as why:
                code = errno.errorcode.get(why.args[0], why.args[0])
                msg = f"couldn't exec {argv[0]}: {code}\n"
                os.write(2, as_bytes('supervisor: ' + msg))

            except Exception:  # noqa
                (file, fun, line), t, v, tbinfo = compact_traceback()
                error = f'{t}, {v}: file: {file} line: {line}'
                msg = f"couldn't exec {exe}: {error}\n"
                os.write(2, as_bytes('supervisor: ' + msg))

            raise RuntimeError('Unreachable')

        finally:
            os.write(2, as_bytes('supervisor: child process was not spawned\n'))
            real_exit(127)  # exit process with code for spawn failure

    def _prepare_child_fds(self, pipes: ProcessPipes) -> None:
        os.dup2(check_not_none(pipes.child_stdin), 0)
        os.dup2(check_not_none(pipes.child_stdout), 1)
        if self.config.redirect_stderr:
            os.dup2(check_not_none(pipes.child_stdout), 2)
        else:
            os.dup2(check_not_none(pipes.child_stderr), 2)

        for i in range(3, self._server_config.minfds):
            if i in self._inherited_fds:
                continue
            close_fd(i)

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
        raise NotFoundError(f"can't find command {exe!r}")

    elif stat.S_ISDIR(st[stat.ST_MODE]):
        raise NotExecutableError(f'command at {exe!r} is a directory')

    elif not (stat.S_IMODE(st[stat.ST_MODE]) & 0o111):
        raise NotExecutableError(f'command at {exe!r} is not executable')

    elif not os.access(exe, os.X_OK):
        raise NoPermissionError(f'no permission to run command {exe!r}')
