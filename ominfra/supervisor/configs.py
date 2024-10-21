import dataclasses as dc
import logging
import signal
import tempfile
import typing as ta

from .datatypes import byte_size
from .datatypes import existing_directory
from .datatypes import existing_dirpath
from .datatypes import logging_level
from .datatypes import octal_type


@dc.dataclass(frozen=True)
class ServerConfig:
    user: str | None = None
    nodaemon: bool = False
    umask: int = 0o22
    directory: str | None = None
    logfile: str = 'supervisord.log'
    logfile_maxbytes: int = 50 * 1024 * 1024
    logfile_backups: int = 10
    loglevel: int = logging.INFO
    pidfile: str = 'supervisord.pid'
    identifier: str = 'supervisor'
    child_logdir: str = '/dev/null'
    minfds: int = 1024
    minprocs: int = 200
    nocleanup: bool = False
    strip_ansi: bool = False
    silent: bool = False

    groups: ta.Sequence['ProcessGroupConfig'] | None = None

    @classmethod
    def new(
            cls,
            umask: int | str = 0o22,
            directory: str | None = None,
            logfile: str = 'supervisord.log',
            logfile_maxbytes: int | str = 50 * 1024 * 1024,
            loglevel: int | str = logging.INFO,
            pidfile: str = 'supervisord.pid',
            child_logdir: str | None = None,
            **kwargs: ta.Any,
    ) -> 'ServerConfig':
        return cls(
            umask=octal_type(umask),
            directory=existing_directory(directory) if directory is not None else None,
            logfile=existing_dirpath(logfile),
            logfile_maxbytes=byte_size(logfile_maxbytes),
            loglevel=logging_level(loglevel),
            pidfile=existing_dirpath(pidfile),
            child_logdir=child_logdir if child_logdir else tempfile.gettempdir(),
            **kwargs,
        )


@dc.dataclass(frozen=True)
class ProcessGroupConfig:
    name: str

    priority: int = 999

    processes: ta.Sequence['ProcessConfig'] | None = None


@dc.dataclass(frozen=True)
class ProcessConfig:
    name: str
    command: str

    uid: int | None = None
    directory: str | None = None
    umask: int | None = None
    priority: int = 999

    autostart: bool = True
    autorestart: str = 'unexpected'

    startsecs: int = 1
    startretries: int = 3

    numprocs: int = 1
    numprocs_start: int = 0

    @dc.dataclass(frozen=True)
    class Log:
        file: str | None = None
        capture_maxbytes: int | None = None
        events_enabled: bool = False
        syslog: bool = False
        backups: int | None = None
        maxbytes: int | None = None

    stdout: Log = Log()
    stderr: Log = Log()

    stopsignal: int = signal.SIGTERM
    stopwaitsecs: int = 10
    stopasgroup: bool = False

    killasgroup: bool = False

    exitcodes: ta.Iterable[int] = (0,)

    redirect_stderr: bool = False

    environment: ta.Mapping[str, str] | None = None
