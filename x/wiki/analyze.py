"""
https://www.mediawiki.org/wiki/Help:Export#Export_format

https://github.com/5j9/wikitextparser
https://github.com/tatuylonen/wikitextprocessor
https://github.com/earwig/mwparserfromhell

https://github.com/WillKoehrsen/wikipedia-data-science/blob/master/notebooks/Downloading%20and%20Parsing%20Wikipedia%20Articles.ipynb

https://en.wikipedia.org/wiki/Help:Wikitext
https://en.wikipedia.org/wiki/Wikipedia:Lua

==

if rev.text and '#invoke' in rev.text.text:
    import wikitextparser as wtp
    parsed = wtp.parse(rev.text.text)
    print(parsed)

    from wikitextprocessor import Wtp
    ctx = Wtp()
    ctx.start_page(page.title)
    tree = ctx.parse(rev.text.text)
    print(tree)

"""
import contextlib
import glob
import io
import os.path
import subprocess
import sys
import time
import typing as ta

import lz4.frame
from omlish import lang  # noqa
from omlish import marshal as msh  # noqa
from omlish.formats import json  # noqa

from . import io as iou
from . import models as mdl


LZ4_JSONL_DIR = os.path.expanduser('~/data/enwiki/json/')


T = ta.TypeVar('T')


class ProgressReporter(ta.Generic[T]):
    def __init__(
            self,
            *,
            fn: ta.Callable[[], T] | None = None,
            start: T | None = None,

            fmt: str | None = None,
            suffix: str | None = None,
            total: T | None = None,
            report_interval: T | None = None,
    ) -> None:
        super().__init__()

        if fn is not None and start is None:
            self._fn = fn
            start = fn()
        elif start is not None and fn is None:
            self._fn = None
        else:
            raise Exception('Must specify either fn or start')

        self._fmt = fmt
        self._suffix = suffix
        self._total_v = total
        self._report_interval_v = report_interval

        self._cur_v = start
        self._start_v = self._cur_v
        self._start_t = time.time()
        self._reported_v: T | None = None
        self._reported_t: float | None = None

    def update(self, cur: T | None = None) -> T:
        if self._fn is not None:
            if cur is not None:
                raise Exception('Must not specify cur when fn given')
            cur = self._fn()
        else:
            if cur is None:
                raise Exception('Must specify cur when fn not given')
        self._cur_v = cur
        return cur

    class Progress(ta.NamedTuple, ta.Generic[T]):
        cur_v: T
        report_base_v: T
        report_elapsed_v: T

        cur_t: float
        report_base_t: float
        report_elapsed_t: float

    def progress(self) -> Progress[T]:
        return ProgressReporter.Progress(
            cur_v=(cur_v := self._cur_v),
            report_base_v=(base_v := self._reported_v if self._reported_v is not None else self._start_v),
            report_elapsed_v=cur_v - base_v,

            cur_t=(cur_t := time.time()),
            report_base_t=(base_t := self._reported_t if self._reported_t is not None else self._start_t),
            report_elapsed_t=cur_t - base_t,
        )

    @property
    def should_report(self) -> bool:
        if self._report_interval_v is None:
            return False
        return self.progress().report_elapsed_v >= self._report_interval_v

    def report(self) -> str:
        prg = self.progress()

        def fmt_v(v: T) -> str:
            if self._fmt is None:
                return str(v)
            return f'{{:{self._fmt}}}'.format(v)  # noqa

        ps = []
        sfx = ' ' + self._suffix if self._suffix is not None else ''
        if self._total_v is not None:
            ps.extend([
                f'{fmt_v(prg.cur_v)} / {fmt_v(self._total_v)}' + sfx,
                f'{prg.cur_v / self._total_v * 100.:.02f} %',
            ])
        else:
            ps.append(f'{fmt_v(self._cur_v)}' + sfx)
        ps.append(
            f'{fmt_v(type(prg.cur_v)(prg.report_elapsed_v / prg.report_elapsed_t))} '
            f'{self._suffix if self._suffix is not None else ""}/s'
        )
        ret = ', '.join(ps)

        self._reported_v = prg.cur_v
        self._reported_t = prg.cur_t

        return ret


def _main() -> None:
    for fn in glob.glob(os.path.join(LZ4_JSONL_DIR, '*.jsonl.lz4')):
        print(fn)
        with contextlib.ExitStack() as es:
            f = es.enter_context(open(fn, 'rb'))
            # fpr = iou.FileProgressReporter(f, time_interval=5)

            # proc = subprocess.Popen(['lz4', '-cdk', fn], stdout=subprocess.PIPE)
            # f = proc.stdout
            # fpr = None

            zf = es.enter_context(lz4.frame.open(f))
            tw = io.TextIOWrapper(zf, 'utf-8')

            fpr0 = ProgressReporter[int](
                fn=f.tell,
                total=os.fstat(f.fileno()).st_size,
                fmt='_',
                suffix='B',
                report_interval=10_000_000,
            )
            fpr1 = ProgressReporter[int](
                start=0,
                fmt='_',
                suffix='pages',
            )

            i = 0
            while (l := tw.readline()):
                i += 1

                fpr0.update()
                fpr1.update(i)
                if fpr0.should_report or fpr1.should_report:
                    print(fpr0.report(), file=sys.stderr)
                    print(fpr1.report(), file=sys.stderr)

                # if fpr is not None and fpr.report():  # noqa
                #     print(f'{i} pages', file=sys.stderr)

                page = msh.unmarshal(json.loads(l), mdl.Page)  # noqa
                # print(page)


if __name__ == '__main__':
    _main()
