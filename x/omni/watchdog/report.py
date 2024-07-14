import logging
import os
import sys
import threading
import traceback
import typing as ta

from .. import dataclasses as dc
from .. import json
from .. import lang
from .. import revision
from .types import Meta
from .types import Report
from .types import Reporter
from .types import ThreadReport
from .types import ThreadReportFrame
from .types import Watch
from .types import Watchdog
from .types import WatchReport


log = logging.getLogger(__name__)


PY_PREFIX = '$PY'
SITE_PREFIX = '$SITE'
SELF_PREFIX = '$SELF'


@lang.cached_nullary
def default_source_prefix_replacements() -> ta.Mapping[str, str]:
    ret: ta.Dict[str, str] = {}

    def get_mod_prefix(mod, splits=1) -> ta.Optional[str]:
        try:
            path = mod.__file__
            if not os.path.isfile(path):
                return None
            path = os.path.abspath(path)
            if not path.endswith('.py'):
                return None
            for _ in range(splits):
                path = os.path.split(path)[0]
            if not path:
                return None
            return path + os.sep
        except Exception:  # noqa
            return None

    from .. import watchdog
    site_prefix = get_mod_prefix(watchdog, 3)
    if site_prefix is not None:
        ret[site_prefix] = SITE_PREFIX + os.sep

    py_prefix = get_mod_prefix(os)
    if py_prefix is not None:
        ret[py_prefix] = PY_PREFIX + os.sep

    def get_self_prefix() -> ta.Optional[str]:
        try:
            if __name__ == '__main__':
                return None
            name_parts = __name__.split('.')
            if name_parts[-1] != 'report':
                return None
            file_parts = os.path.abspath(__file__).split(os.sep)
            if (
                    file_parts[-1] != 'report.py' or
                    len(file_parts) <= len(name_parts) or
                    name_parts[:-1] != file_parts[-len(name_parts):-1]
            ):
                return None
            return os.sep.join(file_parts[:-len(name_parts)]) + os.sep
        except Exception:  # noqa
            return None

    self_prefix = get_self_prefix()
    if self_prefix is not None:
        ret[self_prefix] = SELF_PREFIX + os.sep

    return ret


@lang.cached_nullary
def default_meta() -> Meta:
    return {
        'revision': revision.get_revision(),
    }


class ReporterImpl(Reporter):

    def __init__(
            self,
            *,
            source_prefix_replacements: ta.Optional[ta.Mapping[str, str]] = None,
            meta: ta.Union[Meta, ta.Optional[ta.Callable[[], Meta]]] = None,
    ) -> None:
        super().__init__()

        if source_prefix_replacements is None:
            source_prefix_replacements = default_source_prefix_replacements()
        self._source_prefix_replacements = source_prefix_replacements

        if meta is None:
            meta = default_meta()
        self._meta = meta

    def build_watch_report(self, watch: Watch) -> WatchReport:
        obj = watch.obj
        return WatchReport(
            thread_ident=watch.thread_ident,
            obj_id=watch.obj_id,
            obj_repr=repr(obj) if obj is not None else None,
            age=watch.age,
            staleness=watch.staleness,
            suspended=watch.suspended,
        )

    def build_thread_report(
            self,
            thread: threading.Thread,
            *,
            frames: ta.Mapping[int, ta.Any],
    ) -> ThreadReport:
        if frames is None:
            frames = sys._current_frames()

        rep_stack = None
        try:
            thread_frame = frames[thread.ident]
        except KeyError:
            pass
        else:
            stack = traceback.extract_stack(thread_frame)
            rep_stack = []
            for frame in stack:
                filename = os.path.abspath(frame.filename)
                for prefix, repl in self._source_prefix_replacements.items():
                    if filename.startswith(prefix):
                        filename = repl + filename[len(prefix):]
                        break
                rep_stack.append(ThreadReportFrame(filename, frame.lineno, frame.name))

        return ThreadReport(
            ident=thread.ident,
            name=thread.name,
            stack=rep_stack,
        )

    def build_thread_reports(self) -> ta.Dict[int, ThreadReport]:
        ret = {}

        threads = sorted(threading.enumerate(), key=lambda o: o.ident)
        frames = sys._current_frames()  # noqa
        for thread in threads:
            ret[thread.ident] = self.build_thread_report(thread, frames=frames)

        return ret

    def build_report(
            self,
            watchdog: Watchdog,
            *,
            watches: ta.Set[Watch] = None,
            violations: ta.Set[Watch] = None,
    ) -> Report:
        if watches is None:
            watches = watchdog.current
        if violations is None:
            violations = set()

        violation_reports = [
            self.build_watch_report(w)
            for w in sorted(violations, key=lambda o: o.thread_ident)
        ]
        other_reports = [
            self.build_watch_report(w)
            for w in sorted(watches, key=lambda o: o.thread_ident)
            if w not in violations
        ]
        thread_reports = sorted(self.build_thread_reports().values(), key=lambda o: o.ident)

        meta = self._meta
        if callable(meta):
            meta = meta()

        return Report(
            violations=violation_reports,
            others=other_reports,
            threads=thread_reports,
            meta=meta,
        )

    def format_report(self, report: Report) -> ta.List[str]:
        lines: ta.List[str] = []

        for key, watches in [
            ('violations', report.violations),
            ('others', report.others)
        ]:
            if not watches:
                continue
            dct = {key: [dc.asdict(w) for w in watches]}
            lines.append(json.dumps(dct))

        for thread in report.threads:
            lines.append(json.dumps(dc.asdict(thread)))

        if report.meta:
            lines.append(json.dumps(report.meta))

        return lines

    def report_violations(
            self,
            watchdog: Watchdog,
            watches: ta.Set[Watch],
            violations: ta.Set[Watch],
    ) -> None:
        report = self.build_report(
            watchdog,
            watches=watches,
            violations=violations,
        )

        formatted_report = self.format_report(report)
        for line in formatted_report:
            log.error(line)
