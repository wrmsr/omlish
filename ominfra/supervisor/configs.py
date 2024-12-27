# ruff: noqa: UP007
import dataclasses as dc
import logging
import signal
import tempfile
import typing as ta

from omlish.configs.processing.names import build_config_named_children
from omlish.configs.types import ConfigMap

from .utils.fs import check_existing_dir
from .utils.fs import check_path_with_existing_dir
from .utils.strings import parse_bytes_size
from .utils.strings import parse_octal


##


class RestartWhenExitUnexpected:
    pass


class RestartUnconditionally:
    pass


##


@dc.dataclass(frozen=True)
class ProcessConfig:
    # A Python string expression that is used to compose the supervisor process name for this process. You usually don't
    # need to worry about setting this unless you change numprocs. The string expression is evaluated against a
    # dictionary that includes group_name, host_node_name, process_num, program_name, and here (the directory of the
    # supervisord config file).
    name: str

    # The command that will be run when this program is started. The command can be either absolute (e.g.
    # /path/to/programname) or relative (e.g. programname). If it is relative, the supervisord's environment $PATH will
    # be searched for the executable. Programs can accept arguments, e.g. /path/to/program foo bar. The command line can
    # use double quotes to group arguments with spaces in them to pass to the program, e.g. /path/to/program/name -p
    # "foo bar". Note that the value of command may include Python string expressions, e.g. /path/to/programname
    # --port=80%(process_num)02d might expand to /path/to/programname --port=8000 at runtime. String expressions are
    # evaluated against a dictionary containing the keys group_name, host_node_name, program_name, process_num,
    # numprocs, here (the directory of the supervisord config file), and all supervisord's environment variables
    # prefixed with ENV_. Controlled programs should themselves not be daemons, as supervisord assumes it is responsible
    # for daemonizing its subprocesses
    command: str

    #

    # Supervisor will start as many instances of this program as named by numprocs. Note that if numprocs > 1, the
    # process_name expression must include %(process_num)s (or any other valid Python string expression that includes
    # process_num) within it.
    num_procs: int = 1

    # An integer offset that is used to compute the number at which process_num starts.
    num_procs_start: int = 0

    #

    # Instruct supervisord to use this UNIX user account as the account which runs the program. The user can only be
    # switched if supervisord is run as the root user. If supervisord can't switch to the specified user, the program
    # will not be started.
    #
    # Note: The user will be changed using setuid only. This does not start a login shell and does not change
    # environment variables like USER or HOME
    user: ta.Optional[str] = None
    uid: ta.Optional[int] = None

    # An octal number (e.g. 002, 022) representing the umask of the process.
    umask: ta.Optional[int] = None

    #

    # A file path representing a directory to which supervisord should temporarily chdir before exec'ing the child.
    directory: ta.Optional[str] = None

    # A list of key/value pairs in the form KEY="val",KEY2="val2" that will be placed in the child process' environment.
    # The environment string may contain Python string expressions that will be evaluated against a dictionary
    # containing group_name, host_node_name, process_num, program_name, and here (the directory of the supervisord
    # config file). Values containing non-alphanumeric characters should be quoted (e.g. KEY="val:123",KEY2="val,456").
    # Otherwise, quoting the values is optional but recommended. Note that the subprocess will inherit the environment
    # variables of the shell used to start “supervisord” except for the ones overridden here.
    environment: ta.Optional[ta.Mapping[str, str]] = None

    #

    # The relative priority of the program in the start and shutdown ordering. Lower priorities indicate programs that
    # start first and shut down last at startup and when aggregate commands are used in various clients (e.g. “start
    # all”/”stop all”). Higher priorities indicate programs that start last and shut down first.
    priority: int = 999

    # If true, this program will start automatically when supervisord is started.
    auto_start: bool = True

    # Specifies if supervisord should automatically restart a process if it exits when it is in the RUNNING state. May
    # be one of false, unexpected, or true. If false, the process will not be autorestarted. If unexpected, the process
    # will be restarted when the program exits with an exit code that is not one of the exit codes associated with this
    # process' configuration (see exitcodes). If true, the process will be unconditionally restarted when it exits,
    # without regard to its exit code.
    #
    # Note: autorestart controls whether supervisord will autorestart a program if it exits after it has successfully
    # started up (the process is in the RUNNING state). supervisord has a different restart mechanism for when the
    # process is starting up (the process is in the STARTING state). Retries during process startup are controlled by
    # startsecs and startretries.
    auto_restart: str = 'unexpected'

    # The total number of seconds which the program needs to stay running after a startup to consider the start
    # successful (moving the process from the STARTING state to the RUNNING state). Set to 0 to indicate that the
    # program needn't stay running for any particular amount of time.
    #
    # Note: Even if a process exits with an “expected” exit code (see exitcodes), the start will still be considered a
    # failure if the process exits quicker than startsecs.
    start_secs: int = 1

    # The number of serial failure attempts that supervisord will allow when attempting to start the program before
    # giving up and putting the process into an FATAL state.
    #
    # Note: After each failed restart, process will be put in BACKOFF state and each retry attempt will take
    # increasingly more time.
    start_retries: int = 3

    # The signal used to kill the program when a stop is requested. This can be specified using the signal's name or its
    # number. It is normally one of: TERM, HUP, INT, QUIT, KILL, USR1, or USR2.
    stop_signal: int = signal.SIGTERM

    # The number of seconds to wait for the OS to return a SIGCHLD to supervisord after the program has been sent a
    # stopsignal. If this number of seconds elapses before supervisord receives a SIGCHLD from the process, supervisord
    # will attempt to kill it with a final SIGKILL.
    stop_wait_secs: int = 10

    # If true, the flag causes supervisor to send the stop signal to the whole process group and implies killasgroup is
    # true. This is useful for programs, such as Flask in debug mode, that do not propagate stop signals to their
    # children, leaving them orphaned.
    stop_as_group: bool = False

    # If true, when resorting to send SIGKILL to the program to terminate it send it to its whole process group instead,
    # taking care of its children as well, useful e.g with Python programs using multiprocessing.
    kill_as_group: bool = False

    # The list of “expected” exit codes for this program used with autorestart. If the autorestart parameter is set to
    # unexpected, and the process exits in any other way than as a result of a supervisor stop request, supervisord will
    # restart the process if it exits with an exit code that is not defined in this list.
    #
    # Note: In Supervisor versions prior to 4.0, the default was 0,2. In Supervisor 4.0, the default was changed to 0.
    exitcodes: ta.Sequence[int] = (0,)

    #

    @dc.dataclass(frozen=True)
    class Log:
        file: ta.Optional[str] = None
        capture_max_bytes: ta.Optional[int] = None
        events_enabled: bool = False
        syslog: bool = False
        backups: ta.Optional[int] = None
        max_bytes: ta.Optional[int] = None

    stdout: Log = Log()
    stderr: Log = Log()

    # If true, cause the process' stderr output to be sent back to supervisord on its stdout file descriptor (in UNIX
    # shell terms, this is the equivalent of executing /the/program 2>&1).
    #
    # Note: Do not set redirect_stderr=true in an [eventlistener:x] section. Eventlisteners use stdout and stdin to
    # communicate with supervisord. If stderr is redirected, output from stderr will interfere with the eventlistener
    # protocol.
    redirect_stderr: bool = False


@dc.dataclass(frozen=True)
class ProcessGroupConfig:
    name: str

    priority: int = 999

    processes: ta.Optional[ta.Sequence[ProcessConfig]] = None


@dc.dataclass(frozen=True)
class ServerConfig:
    # Instruct supervisord to switch users to this UNIX user account before doing any meaningful processing. The user
    # can only be switched if supervisord is started as the root user.
    user: ta.Optional[str] = None

    # If true, supervisord will start in the foreground instead of daemonizing.
    nodaemon: bool = False

    # The umask of the supervisord process.
    umask: int = 0o22

    #

    # When supervisord daemonizes, switch to this directory. This option can include the value %(here)s, which expands
    # to the directory in which the supervisord configuration file was found.
    directory: ta.Optional[str] = None

    # The location in which supervisord keeps its pid file. This option can include the value %(here)s, which expands to
    # the directory in which the supervisord configuration file was found.
    pidfile: str = 'supervisord.pid'

    # The identifier string for this supervisor process, used by the RPC interface.
    identifier: str = 'supervisor'

    # The minimum number of file descriptors that must be available before supervisord will start successfully.
    min_fds: int = 1024
    # The minimum number of process descriptors that must be available before supervisord will start successfully.
    min_procs: int = 200

    # Prevent supervisord from clearing any existing AUTO child log files at startup time. Useful for debugging
    nocleanup: bool = False

    # Strip all ANSI escape sequences from child log files.
    strip_ansi: bool = False

    #

    # The path to the activity log of the supervisord process. This option can include the value %(here)s, which expands
    # to the directory in which the supervisord configuration file was found.
    logfile: str = 'supervisord.log'

    # The maximum number of bytes that may be consumed by the activity log file before it is rotated (suffix multipliers
    # like “KB”, “MB”, and “GB” can be used in the value). Set this value to 0 to indicate an unlimited log size.
    logfile_max_bytes: int = 50 * 1024 * 1024

    # The number of backups to keep around resulting from activity log file rotation. If set to 0, no backups will be
    # kept.
    logfile_backups: int = 10

    # The logging level, dictating what is written to the supervisord activity log. One of critical, error, warn, info,
    # debug, trace, or blather. Note that at log level debug, the supervisord log file will record the stderr/stdout
    # output of its child processes and extended info about process state changes, which is useful for debugging a
    # process which isn't starting properly.
    loglevel: int = logging.INFO

    # The directory used for AUTO child log files. This option can include the value %(here)s, which expands to the
    # directory in which the supervisord configuration file was found.
    child_logdir: str = '/dev/null'

    # If true and not daemonized, logs will not be directed to stdout.
    silent: bool = False

    #

    groups: ta.Optional[ta.Sequence[ProcessGroupConfig]] = None

    # TODO: implement - make sure to accept broken symlinks
    group_config_dirs: ta.Optional[ta.Sequence[str]] = None

    #

    http_port: ta.Optional[int] = None

    #

    @classmethod
    def new(
            cls,
            *,
            umask: ta.Union[int, str] = 0o22,
            directory: ta.Optional[str] = None,
            logfile: str = 'supervisord.log',
            logfile_max_bytes: ta.Union[int, str] = 50 * 1024 * 1024,
            loglevel: ta.Union[int, str] = logging.INFO,
            pidfile: str = 'supervisord.pid',
            child_logdir: ta.Optional[str] = None,
            **kwargs: ta.Any,
    ) -> 'ServerConfig':
        return cls(
            umask=parse_octal(umask),
            directory=check_existing_dir(directory) if directory is not None else None,
            logfile=check_path_with_existing_dir(logfile),
            logfile_max_bytes=parse_bytes_size(logfile_max_bytes),
            loglevel=parse_logging_level(loglevel),
            pidfile=check_path_with_existing_dir(pidfile),
            child_logdir=child_logdir if child_logdir else tempfile.gettempdir(),
            **kwargs,
        )


##


def prepare_process_group_config(dct: ConfigMap) -> ConfigMap:
    out = dict(dct)
    out['processes'] = build_config_named_children(out.get('processes'))
    return out


def prepare_server_config(dct: ta.Mapping[str, ta.Any]) -> ta.Mapping[str, ta.Any]:
    out = dict(dct)
    group_dcts = build_config_named_children(out.get('groups'))
    out['groups'] = [prepare_process_group_config(group_dct) for group_dct in group_dcts or []]
    return out


##


def parse_logging_level(value: ta.Union[str, int]) -> int:
    if isinstance(value, int):
        return value
    s = str(value).lower()
    level = logging.getLevelNamesMapping().get(s.upper())
    if level is None:
        raise ValueError(f'bad logging level name {value!r}')
    return level
