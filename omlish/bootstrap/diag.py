# ruff: noqa: UP007
import contextlib
import dataclasses as dc
import signal
import sys
import typing as ta

from .. import lang
from .base import Bootstrap
from .base import ContextBootstrap


if ta.TYPE_CHECKING:
    import cProfile  # noqa
    import pstats

    from ..diag import threads as diagt

else:
    cProfile = lang.proxy_import('cProfile')  # noqa
    pstats = lang.proxy_import('pstats')

    diagt = lang.proxy_import('..diag.threads', __package__)


##


class ProfilingBootstrap(ContextBootstrap['ProfilingBootstrap.Config']):
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
