import logging
import tempfile
import typing as ta

from omlish import dataclasses as dc

from .datatypes import byte_size
from .datatypes import existing_directory
from .datatypes import existing_dirpath
from .datatypes import logging_level
from .datatypes import octal_type


@dc.dataclass(frozen=True)
class ServerConfig:
    def add(
            self,
            name=None,  # attribute name on self
            confname=None,  # dotted config path name
            short=None,  # short option name
            long=None,  # long option name

            handler=None,  # handler (defaults to string)
            default=None,  # default value
            required=None,  # message if not provided
            flag=None,  # if not None, flag value
            env=None,  # if not None, environment variable
    ):
        pass

    user: str | None = None
    nodaemon: bool = False
    umask: int = dc.xfield(0o22, coerce=octal_type)
    directory: str | None = dc.xfield(None, coerce=existing_directory)
    logfile: str = dc.xfield('supervisord.log', coerce=existing_dirpath)
    logfile_maxbytes: int = dc.xfield(50 * 1024 * 1024, coerce=byte_size)
    logfile_backups: int = dc.xfield(10)
    loglevel: int = dc.xfield(logging.INFO, coerce=logging_level)
    pidfile: str = dc.xfield('supervisord.pid', coerce=existing_dirpath)
    identifier: str = dc.xfield('supervisor')
    child_logdir = dc.xfield(default_factory=lambda: tempfile.gettempdir(), coerce=existing_directory)
    minfds: int = 1024
    minprocs: int = 200
    nocleanup: bool = False
    strip_ansi: bool = False
    silent: bool = False


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

    stopsignal: str = 'TERM'
    stopwaitsecs: int = 10
    stopasgroup: bool = False

    killasgroup: bool = False

    exitcodes: ta.Iterable[int] = (0,)

    redirect_stderr: bool = False

    environment: ta.Mapping[str, str] | None = None
