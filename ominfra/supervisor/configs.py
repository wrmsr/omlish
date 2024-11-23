# ruff: noqa: UP007
import dataclasses as dc
import logging
import signal
import tempfile
import typing as ta

from ..configs import ConfigMapping
from ..configs import build_config_named_children
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
    name: str
    command: str

    uid: ta.Optional[int] = None
    directory: ta.Optional[str] = None
    umask: ta.Optional[int] = None
    priority: int = 999

    autostart: bool = True
    autorestart: str = 'unexpected'

    startsecs: int = 1
    startretries: int = 3

    numprocs: int = 1
    numprocs_start: int = 0

    @dc.dataclass(frozen=True)
    class Log:
        file: ta.Optional[str] = None
        capture_maxbytes: ta.Optional[int] = None
        events_enabled: bool = False
        syslog: bool = False
        backups: ta.Optional[int] = None
        maxbytes: ta.Optional[int] = None

    stdout: Log = Log()
    stderr: Log = Log()

    stopsignal: int = signal.SIGTERM
    stopwaitsecs: int = 10
    stopasgroup: bool = False

    killasgroup: bool = False

    exitcodes: ta.Sequence[int] = (0,)

    redirect_stderr: bool = False

    environment: ta.Optional[ta.Mapping[str, str]] = None


@dc.dataclass(frozen=True)
class ProcessGroupConfig:
    name: str

    priority: int = 999

    processes: ta.Optional[ta.Sequence[ProcessConfig]] = None


@dc.dataclass(frozen=True)
class ServerConfig:
    user: ta.Optional[str] = None
    nodaemon: bool = False
    umask: int = 0o22
    directory: ta.Optional[str] = None
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

    groups: ta.Optional[ta.Sequence[ProcessGroupConfig]] = None

    @classmethod
    def new(
            cls,
            umask: ta.Union[int, str] = 0o22,
            directory: ta.Optional[str] = None,
            logfile: str = 'supervisord.log',
            logfile_maxbytes: ta.Union[int, str] = 50 * 1024 * 1024,
            loglevel: ta.Union[int, str] = logging.INFO,
            pidfile: str = 'supervisord.pid',
            child_logdir: ta.Optional[str] = None,
            **kwargs: ta.Any,
    ) -> 'ServerConfig':
        return cls(
            umask=parse_octal(umask),
            directory=check_existing_dir(directory) if directory is not None else None,
            logfile=check_path_with_existing_dir(logfile),
            logfile_maxbytes=parse_bytes_size(logfile_maxbytes),
            loglevel=parse_logging_level(loglevel),
            pidfile=check_path_with_existing_dir(pidfile),
            child_logdir=child_logdir if child_logdir else tempfile.gettempdir(),
            **kwargs,
        )


##


def prepare_process_group_config(dct: ConfigMapping) -> ConfigMapping:
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
