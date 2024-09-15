# ruff: noqa: UP007
import contextlib
import dataclasses as dc
import signal
import sys
import threading
import typing as ta

from .. import check
from .. import lang
from .base import Bootstrap
from .base import ContextBootstrap
from .base import SimpleBootstrap


if ta.TYPE_CHECKING:
    import cProfile  # noqa
    import pstats

    from ..diag import pycharm as diagpc
    from ..diag import replserver as diagrs
    from ..diag import threads as diagt

else:
    cProfile = lang.proxy_import('cProfile')  # noqa
    pstats = lang.proxy_import('pstats')

    diagpc = lang.proxy_import('..diag.pycharm', __package__)
    diagrs = lang.proxy_import('..diag.replserver', __package__)
    diagt = lang.proxy_import('..diag.threads', __package__)


##


class CheckBootstrap(ContextBootstrap['CheckBootstrap.Config']):
    @dc.dataclass(frozen=True)
    class Config(Bootstrap.Config):
        breakpoint: bool = False

    @staticmethod
    def _breakpoint(exc: Exception) -> None:  # noqa
        breakpoint()  # noqa

    @contextlib.contextmanager
    def enter(self) -> ta.Iterator[None]:
        if not self._config.breakpoint:
            return

        check.register_on_raise(CheckBootstrap._breakpoint)
        try:
            yield
        finally:
            check.unregister_on_raise(CheckBootstrap._breakpoint)


##


class CprofileBootstrap(ContextBootstrap['CprofileBootstrap.Config']):
    @dc.dataclass(frozen=True)
    class Config(Bootstrap.Config):
        enable: bool = False
        builtins: bool = True

        outfile: ta.Optional[str] = None

        print: bool = False
        sort: str = 'cumtime'
        topn: int = 100

    @contextlib.contextmanager
    def enter(self) -> ta.Iterator[None]:
        if not self._config.enable:
            yield
            return

        prof = cProfile.Profile()
        prof.enable()
        try:
            yield

        finally:
            prof.disable()
            prof.create_stats()

            if self._config.print:
                pstats.Stats(prof) \
                    .strip_dirs() \
                    .sort_stats(self._config.sort) \
                    .print_stats(self._config.topn)

            if self._config.outfile is not None:
                prof.dump_stats(self._config.outfile)


##


class ThreadDumpBootstrap(ContextBootstrap['ThreadDumpBootstrap.Config']):
    @dc.dataclass(frozen=True)
    class Config(Bootstrap.Config):
        interval_s: ta.Optional[float] = None
        nodaemon: bool = False

        on_sigquit: bool = False

    @contextlib.contextmanager
    def enter(self) -> ta.Iterator[None]:
        if self._config.interval_s:
            tdt = diagt.create_thread_dump_thread(
                interval_s=self._config.interval_s,
                start=True,
                nodaemon=self._config.nodaemon,
            )
        else:
            tdt = None

        if self._config.on_sigquit:
            dump_threads_str = diagt.dump_threads_str

            def handler(signum, frame):
                print(dump_threads_str(), file=sys.stderr)

            prev_sq = lang.just(signal.signal(signal.SIGQUIT, handler))
        else:
            prev_sq = lang.empty()

        try:
            yield

        finally:
            if tdt is not None and not self._config.nodaemon:
                tdt.stop_nowait()

            if prev_sq.present:
                signal.signal(signal.SIGQUIT, prev_sq.must())


##


class TimebombBootstrap(ContextBootstrap['TimebombBootstrap.Config']):
    @dc.dataclass(frozen=True)
    class Config(Bootstrap.Config):
        delay_s: ta.Optional[float] = None

    @contextlib.contextmanager
    def enter(self) -> ta.Iterator[None]:
        if not self._config.delay_s:
            yield
            return

        tbt = diagt.create_timebomb_thread(
            self._config.delay_s,
            start=True,
        )
        try:
            yield
        finally:
            tbt.stop_nowait()


##


class PycharmBootstrap(SimpleBootstrap['PycharmBootstrap.Config']):
    @dc.dataclass(frozen=True)
    class Config(Bootstrap.Config):
        debug_host: ta.Optional[str] = None
        debug_port: ta.Optional[int] = None
        version: ta.Optional[str] = None

    def run(self) -> None:
        if self._config.debug_port is not None:
            diagpc.pycharm_remote_debugger_attach(
                self._config.debug_host,
                self._config.debug_port,
                version=self._config.version,
            )


##


class ReplServerBootstrap(ContextBootstrap['ReplServerBootstrap.Config']):
    @dc.dataclass(frozen=True)
    class Config(Bootstrap.Config):
        path: str | None = None

    @contextlib.contextmanager
    def enter(self) -> ta.Iterator[None]:
        if self._config.path is None:
            return

        with diagrs.ReplServer(diagrs.ReplServer.Config(
            path=self._config.path,
        )) as rs:
            thread = threading.Thread(target=rs.run, name='replserver')
            thread.start()

            yield
