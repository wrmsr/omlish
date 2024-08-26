"""
TODO:
 - pydevd connect-back
 - (more) logging
 - env vars, files
 - repl server
 - packaging fixups
 - profiling
 - pidfile
 - daemonize
 - sigquit thread/coro dump + pdb enter
 - option to install in pdb? *or* entrypoint ala runmodule.py
"""
import abc
import contextlib
import dataclasses as dc
import enum
import faulthandler
import gc
import logging
import os
import pwd
import resource
import typing as ta

from omlish import lang
from omlish import logs


if ta.TYPE_CHECKING:
    from omlish import libc
else:
    libc = lang.proxy_import('omlish.libc')


BootstrapConfigT = ta.TypeVar('BootstrapConfigT', bound='Bootstrap.Config')


##


class Bootstrap(abc.ABC, ta.Generic[BootstrapConfigT]):
    @dc.dataclass(frozen=True)
    class Config(abc.ABC):
        pass

    def __init__(self, config: BootstrapConfigT) -> None:
        super().__init__()
        self._config = config

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)
        if abc.ABC not in cls.__bases__ and not issubclass(cls.__dict__['Config'], Bootstrap.Config):
            raise TypeError(cls)


class SimpleBootstrap(Bootstrap[BootstrapConfigT], abc.ABC):
    @abc.abstractmethod
    def run(self) -> None:
        raise NotImplementedError


class ContextBootstrap(Bootstrap[BootstrapConfigT], abc.ABC):
    @abc.abstractmethod
    def enter(self) -> ta.ContextManager[None]:
        raise NotImplementedError


##


class CwdBootstrap(ContextBootstrap['CwdBootstrap.Config']):
    @dc.dataclass(frozen=True)
    class Config(Bootstrap.Config):
        path: str | None = None

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
        setuid: str | None = None

    def run(self) -> None:
        if self._config.setuid is not None:
            user = pwd.getpwnam(self._config.setuid)
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
        debug: int | None = None

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
        nice: int | None = None

    def run(self) -> None:
        if self._config.nice is not None:
            os.nice(self._config.nice)


##


class LogBootstrap(ContextBootstrap['LogBootstrap.Config']):
    @dc.dataclass(frozen=True)
    class Config(Bootstrap.Config):
        level: str | int
        json: bool = False

    @contextlib.contextmanager
    def enter(self) -> ta.Iterator[None]:
        if self._config.level is not None:
            handler = logs.configure_standard_logging(
                self._config.level,
                json=self._config.json,
            )
        else:
            handler = None

        try:
            yield

        finally:
            if handler is not None:
                logging.root.removeHandler(handler)


##


class FaulthandlerBootstrap(ContextBootstrap['FaulthandlerBootstrap.Config']):
    @dc.dataclass(frozen=True)
    class Config(Bootstrap.Config):
        enabled: bool = False

    @contextlib.contextmanager
    def enter(self) -> ta.Iterator[None]:
        if self._config.enabled is not None:
            prev = faulthandler.is_enabled()
            if self._config.enabled:
                faulthandler.enable()
            else:
                faulthandler.disable()
        else:
            prev = None

        try:
            yield

        finally:
            if prev is True:
                faulthandler.enable()
            elif prev is False:
                faulthandler.disable()


##


class PrctlBootstrap(SimpleBootstrap['PrctlBootstrap.Config']):
    @dc.dataclass(frozen=True)
    class Config(Bootstrap.Config):
        dumpable: bool = False
        deathsig: bool | int | None = False

    def run(self) -> None:
        if self._config.dumpable:
            libc.prctl(libc.PR_SET_DUMPABLE, 1, 0, 0, 0, 0)

        if self._config.deathsig not in (None, False):
            sig = self._config.prctl_deathsig if isinstance(self._config.prctl_deathsig, int) else signal.SIGTERM  # noqa
            libc.prctl(libc.PR_SET_PDEATHSIG, sig, 0, 0, 0, 0)


##


RLIMITS_BY_NAME = {
    a: v  # noqa
    for a in dir(resource)
    if a.startswith('RLIMIT_')
    and a == a.upper()
    and isinstance((v := getattr(a)), int)
}


class RlimitBootstrap(ContextBootstrap['RlimitBootstrap.Config']):
    @dc.dataclass(frozen=True)
    class Config(Bootstrap.Config):
        limits: ta.Mapping[str, tuple[int | None, int | None]] | None = None

    @contextlib.contextmanager
    def enter(self) -> ta.Iterator[None]:
        if self._config.limits:
            def or_infin(l: int | None) -> int:
                return l if l is not None else resource.RLIM_INFINITY

            prev = {}
            for k, (s, h) in self._config.limits.items():
                i = RLIMITS_BY_NAME[k.upper()]
                prev[i] = resource.getrlimit(i)
                resource.setrlimit(i, (or_infin(s), or_infin(h)))

        else:
            prev = None

        try:
            yield

        finally:
            if prev is not None:
                for k, v in prev.items():
                    resource.setrlimit(k, v)


##


class BootstrapHarness:
    def __init__(self, lst: ta.Sequence[Bootstrap]) -> None:
        super().__init__()
        self._lst = lst

    @contextlib.contextmanager
    def __call__(self) -> ta.Iterator[None]:
        with contextlib.ExitStack() as es:
            for c in self._lst:
                if isinstance(c, SimpleBootstrap):
                    c.run()
                elif isinstance(c, ContextBootstrap):
                    es.enter_context(c.enter())
                else:
                    raise TypeError(c)
            yield


##


def _main() -> None:
    with BootstrapHarness([
        CwdBootstrap(CwdBootstrap.Config(
            path='..',
        )),
    ])():
        print(os.getcwd())


if __name__ == '__main__':
    _main()
