# ruff: noqa: UP007 UP045
"""
TODO:
 - execstat equivs
 - put memray junk in a omcore.diag module lol
"""
import collections
import contextlib
import dataclasses as dc
import gc
import json
import os.path
import signal
import sys
import tempfile
import threading
import typing as ta

from .. import check
from .. import lang
from .base import Bootstrap
from .base import ContextBootstrap
from .base import SimpleBootstrap


with lang.auto_proxy_import(globals()):
    import cProfile  # noqa
    import pstats

    import memray

    from ..diag import debug as d_debug
    from ..diag import execstat
    from ..diag import pycharm as d_pycharm
    from ..diag import replserver
    from ..diag import threads as d_threads


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
            tdt = d_threads.create_thread_dump_thread(
                interval_s=self._config.interval_s,
                start=True,
                nodaemon=self._config.nodaemon,
            )
        else:
            tdt = None

        if self._config.on_sigquit:
            dump_threads_str = d_threads.dump_threads_str

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

        tbt = d_threads.create_timebomb_thread(
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
        debug: ta.Optional[str] = None

    def run(self) -> None:
        if self._config.debug is not None:
            prd = d_pycharm.PycharmRemoteDebugger.parse(self._config.debug)
            d_pycharm.pycharm_remote_debugger_attach(prd)


##


class ReplServerBootstrap(ContextBootstrap['ReplServerBootstrap.Config']):
    @dc.dataclass(frozen=True)
    class Config(Bootstrap.Config):
        path: str | None = None

    @contextlib.contextmanager
    def enter(self) -> ta.Iterator[None]:
        if self._config.path is None:
            return

        with replserver.ReplServer(replserver.ReplServer.Config(
            path=self._config.path,
        )) as rs:
            thread = threading.Thread(target=rs.run, name='replserver')
            thread.start()

            yield


##


class DebugBootstrap(ContextBootstrap['DebugBootstrap.Config']):
    @dc.dataclass(frozen=True)
    class Config(Bootstrap.Config):
        enable: bool = False

    @contextlib.contextmanager
    def enter(self) -> ta.Iterator[None]:
        if not self._config.enable:
            return

        with d_debug.debugging_on_exception():
            yield


##


class MemrayBootstrap(ContextBootstrap['MemrayBootstrap.Config']):
    @dc.dataclass(frozen=True)
    class Config(Bootstrap.Config):
        dump: bool = False

    @contextlib.contextmanager
    def enter(self) -> ta.Iterator[None]:
        if not self._config.dump:
            yield

        tmp_dir = tempfile.mkdtemp()
        mr_fp = os.path.join(tmp_dir, 'memray.bin')

        with memray.Tracker(
            mr_fp,
            trace_python_allocators=True,
            track_object_lifetimes=True,
        ) as tracker:
            yield

            for _ in range(3):
                gc.collect()

        survivors = tracker.get_surviving_objects()

        def type_name(obj: ta.Any) -> str:  # noqa
            ty = type(obj)  # noqa
            return f'{ty.__module__}.{ty.__qualname__}'

        counts = collections.Counter(type_name(o) for o in survivors)

        sizes = collections.defaultdict[str, int](int)
        for obj in survivors:
            try:
                sizes[type_name(obj)] += sys.getsizeof(obj)
            except TypeError:
                pass

        for ty, n in counts.most_common(30):
            print(f'{n:>8} {sizes[ty]:>12} {ty}', file=sys.stderr)


##


class ExecstatBootstrap(ContextBootstrap['ExecstatBootstrap.Config']):
    @dc.dataclass(frozen=True)
    class Config(Bootstrap.Config):
        dump: bool = False

    @contextlib.contextmanager
    def enter(self) -> ta.Iterator[None]:
        if not self._config.dump:
            yield

        tracker = execstat.Tracker(
            time=True,
            rss=True,
            modules=True,
        )

        tracker.start()

        try:
            yield

        finally:
            tracker.end()

            report = tracker.report()

            print(json.dumps(report, indent=2, separators=(', ', ': ')), file=sys.stderr)
