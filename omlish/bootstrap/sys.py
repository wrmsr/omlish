# ruff: noqa: UP006 UP007
import contextlib
import dataclasses as dc
import enum
import faulthandler
import gc
import importlib
import logging
import os
import pwd
import resource
import signal
import sys
import typing as ta

from .. import lang
from .base import Bootstrap
from .base import ContextBootstrap
from .base import SimpleBootstrap


if ta.TYPE_CHECKING:
    from .. import libc
    from .. import logs
    from .. import os as osu
    from ..formats import dotenv

else:
    libc = lang.proxy_import('..libc', __package__)
    logs = lang.proxy_import('..logs', __package__)
    osu = lang.proxy_import('..os', __package__)
    dotenv = lang.proxy_import('..formats.dotenv', __package__)


##


class CwdBootstrap(ContextBootstrap['CwdBootstrap.Config']):
    @dc.dataclass(frozen=True)
    class Config(Bootstrap.Config):
        path: ta.Optional[str] = None

    @contextlib.contextmanager
    def enter(self) -> ta.Iterator[None]:
        if self._config.path is not None:
            prev = os.getcwd()
            os.chdir(self._config.path)
        else:
            prev = None

        try:
            yield

        finally:
            if prev is not None:
                os.chdir(prev)


##


class SetuidBootstrap(SimpleBootstrap['SetuidBootstrap.Config']):
    @dc.dataclass(frozen=True)
    class Config(Bootstrap.Config):
        user: ta.Optional[str] = None

    def run(self) -> None:
        if self._config.user is not None:
            user = pwd.getpwnam(self._config.user)
            os.setuid(user.pw_uid)


##


class GcDebugFlag(enum.Enum):
    STATS = gc.DEBUG_STATS
    COLLECTABLE = gc.DEBUG_COLLECTABLE
    UNCOLLECTABLE = gc.DEBUG_UNCOLLECTABLE
    SAVEALL = gc.DEBUG_SAVEALL
    LEAK = gc.DEBUG_LEAK


class GcBootstrap(ContextBootstrap['GcBootstrap.Config']):
    @dc.dataclass(frozen=True)
    class Config(Bootstrap.Config):
        disable: bool = False
        debug: ta.Optional[int] = None

    @contextlib.contextmanager
    def enter(self) -> ta.Iterator[None]:
        prev_enabled = gc.isenabled()
        if self._config.disable:
            gc.disable()

        if self._config.debug is not None:
            prev_debug = gc.get_debug()
            gc.set_debug(self._config.debug)
        else:
            prev_debug = None

        try:
            yield

        finally:
            if prev_enabled:
                gc.enable()

            if prev_debug is not None:
                gc.set_debug(prev_debug)


##


class NiceBootstrap(SimpleBootstrap['NiceBootstrap.Config']):
    @dc.dataclass(frozen=True)
    class Config(Bootstrap.Config):
        nice: ta.Optional[int] = None

    def run(self) -> None:
        if self._config.nice is not None:
            os.nice(self._config.nice)


##


class LogBootstrap(ContextBootstrap['LogBootstrap.Config']):
    @dc.dataclass(frozen=True)
    class Config(Bootstrap.Config):
        level: ta.Union[str, int, None] = None
        json: bool = False

    @contextlib.contextmanager
    def enter(self) -> ta.Iterator[None]:
        if self._config.level is None:
            yield
            return

        handler = logs.configure_standard_logging(
            self._config.level,
            json=self._config.json,
        )

        try:
            yield

        finally:
            if handler is not None:
                logging.root.removeHandler(handler)


##


class FaulthandlerBootstrap(ContextBootstrap['FaulthandlerBootstrap.Config']):
    @dc.dataclass(frozen=True)
    class Config(Bootstrap.Config):
        enabled: ta.Optional[bool] = None

    @contextlib.contextmanager
    def enter(self) -> ta.Iterator[None]:
        if self._config.enabled is None:
            yield
            return

        prev = faulthandler.is_enabled()
        if self._config.enabled:
            faulthandler.enable()
        else:
            faulthandler.disable()

        try:
            yield

        finally:
            if prev:
                faulthandler.enable()
            else:
                faulthandler.disable()


##


SIGNALS_BY_NAME = {
    a[len('SIG'):]: v  # noqa
    for a in dir(signal)
    if a.startswith('SIG')
    and not a.startswith('SIG_')
    and a == a.upper()
    and isinstance((v := getattr(signal, a)), int)
}


class PrctlBootstrap(SimpleBootstrap['PrctlBootstrap.Config']):
    @dc.dataclass(frozen=True)
    class Config(Bootstrap.Config):
        dumpable: bool = False
        deathsig: ta.Union[int, str, None] = None

    def run(self) -> None:
        if self._config.dumpable:
            libc.prctl(libc.PR_SET_DUMPABLE, 1, 0, 0, 0, 0)

        if self._config.deathsig is not None:
            if isinstance(self._config.deathsig, int):
                sig = self._config.deathsig
            else:
                sig = SIGNALS_BY_NAME[self._config.deathsig.upper()]
            libc.prctl(libc.PR_SET_PDEATHSIG, sig, 0, 0, 0, 0)


##


RLIMITS_BY_NAME = {
    a[len('RLIMIT_'):]: v  # noqa
    for a in dir(resource)
    if a.startswith('RLIMIT_')
    and a == a.upper()
    and isinstance((v := getattr(resource, a)), int)
}


class RlimitBootstrap(ContextBootstrap['RlimitBootstrap.Config']):
    @dc.dataclass(frozen=True)
    class Config(Bootstrap.Config):
        limits: ta.Optional[ta.Mapping[str, ta.Tuple[ta.Optional[int], ta.Optional[int]]]] = None

    @contextlib.contextmanager
    def enter(self) -> ta.Iterator[None]:
        if not self._config.limits:
            yield
            return

        def or_infin(l: ta.Optional[int]) -> int:
            return l if l is not None else resource.RLIM_INFINITY

        prev = {}
        for k, (s, h) in self._config.limits.items():
            i = RLIMITS_BY_NAME[k.upper()]
            prev[i] = resource.getrlimit(i)
            resource.setrlimit(i, (or_infin(s), or_infin(h)))

        try:
            yield

        finally:
            for i, (s, h) in prev.items():
                resource.setrlimit(i, (s, h))


##


class ImportBootstrap(SimpleBootstrap['ImportBootstrap.Config']):
    @dc.dataclass(frozen=True)
    class Config(Bootstrap.Config):
        modules: ta.Optional[ta.Sequence[str]] = None

    def run(self) -> None:
        for m in self._config.modules or ():
            importlib.import_module(m)


##


class EnvBootstrap(ContextBootstrap['EnvBootstrap.Config']):
    @dc.dataclass(frozen=True)
    class Config(Bootstrap.Config):
        vars: ta.Optional[ta.Mapping[str, ta.Optional[str]]] = None
        files: ta.Optional[ta.Sequence[str]] = None

    @contextlib.contextmanager
    def enter(self) -> ta.Iterator[None]:
        if not (self._config.vars or self._config.files):
            yield
            return

        new = dict(self._config.vars or {})
        for f in self._config.files or ():
            new.update(dotenv.dotenv_values(f, env=os.environ))

        prev: ta.Dict[str, ta.Optional[str]] = {k: os.environ.get(k) for k in new}

        def do(k: str, v: ta.Optional[str]) -> None:
            if v is not None:
                os.environ[k] = v
            else:
                del os.environ[k]

        for k, v in new.items():
            do(k, v)

        try:
            yield

        finally:
            for k, v in prev.items():
                do(k, v)


##


class PidfileBootstrap(ContextBootstrap['PidfileBootstrap.Config']):
    @dc.dataclass(frozen=True)
    class Config(Bootstrap.Config):
        path: ta.Optional[str] = None

    @contextlib.contextmanager
    def enter(self) -> ta.Iterator[None]:
        if self._config.path is None:
            yield
            return

        with osu.Pidfile(self._config.path) as pf:
            pf.write()
            yield


##


class FdsBootstrap(SimpleBootstrap['FdsBootstrap.Config']):
    @dc.dataclass(frozen=True)
    class Config(Bootstrap.Config):
        redirects: ta.Optional[ta.Mapping[int, ta.Union[int, str, None]]] = None

    def run(self) -> None:
        for dst, src in (self._config.redirects or {}).items():
            if src is None:
                src = '/dev/null'
            if isinstance(src, int):
                os.dup2(src, dst)
            elif isinstance(src, str):
                sfd = os.open(src, os.O_RDWR)
                os.dup2(sfd, dst)
                os.close(sfd)
            else:
                raise TypeError(src)


##


class PrintPidBootstrap(SimpleBootstrap['PrintPidBootstrap.Config']):
    @dc.dataclass(frozen=True)
    class Config(Bootstrap.Config):
        enable: bool = False
        pause: bool = False

    def run(self) -> None:
        if not (self._config.enable or self._config.pause):
            return
        print(str(os.getpid()), file=sys.stderr)
        if self._config.pause:
            input()
