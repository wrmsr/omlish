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
import concurrent.futures as cf
import contextlib
import errno

import fcntl
import glob
import io
import multiprocessing as mp
import os.path
import signal
import sys

import lz4.frame
import mwparserfromhell as mfh  # noqa
import mwparserfromhell.nodes  # noqa
import sqlalchemy as sa
import wikitextparser as wtp0  # noqa

from omlish import concurrent as cfu
from omlish import lang
from omlish import libc
from omlish import marshal as msh
from omlish.formats import json

from . import models as mdl
from .utils.progress import ProgressReporter


LZ4_JSONL_DIR = os.path.expanduser('~/data/enwiki/json/')


meta = sa.MetaData()
pages_table = sa.Table(
    'pages',
    meta,
    sa.Column('id', sa.Integer(), primary_key=True),
    sa.Column('title', sa.String()),
    sa.Column('text', sa.BLOB),
)


def analyze_file(db_url: str, fn: str, pr: int) -> None:
    print(f'pid={os.getpid()} {pr=} {fn}', file=sys.stderr)

    rows: list[dict] = []
    row_batch_size = 1_000

    rb = 0
    cb = 0

    with contextlib.ExitStack() as es:
        engine = sa.create_engine(db_url, echo=True)
        es.enter_context(lang.defer(engine.dispose))

        with engine.begin() as conn:
            meta.create_all(bind=conn)

        def maybe_flush_rows():
            if len(rows) >= row_batch_size:
                with engine.begin() as conn:
                    conn.execute(pages_table.insert(), rows)

                rows.clear()

        f = es.enter_context(open(fn, 'rb'))
        # fpr = iou.FileProgressReporter(f, time_interval=5)

        def check_pr():
            flags = fcntl.fcntl(pr, fcntl.F_GETFL)
            fcntl.fcntl(pr, fcntl.F_SETFL, flags | os.O_NONBLOCK)
            try:
                pbuf = os.read(pr, 1)
            except BlockingIOError:
                return
            except Exception as e:
                print(f'!!! {e=}', file=sys.stderr)
                raise
            if pbuf:
                print(f'!!! READ, SHOULD NOT HAPPEN {pbuf=}', file=sys.stderr)
            else:
                print(f'!!! PIPE CLOSED', file=sys.stderr)
            os.kill(os.getpid(), signal.SIGTERM)
            sys.exit(1)

        maybe_check_pr = lang.periodically(check_pr, 3.)

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
            report_interval=1_000_000,
        )
        fpr1 = ProgressReporter[int](
            start=0,
            fmt='_',
            suffix='pages',
        )

        i = 0
        while (l := tw.readline()):
            i += 1

            maybe_check_pr()

            fpr0.update()
            fpr1.update(i)
            if fpr0.should_report or fpr1.should_report:
                print(', '.join([*fpr0.report(), *fpr1.report()]), file=sys.stderr)
                print(f'{rb:_} B raw, {cb:_} B cpr, {cb / rb * 100.:.02f} %', file=sys.stderr)
                rb = cb = 0

            # if fpr is not None and fpr.report():  # noqa
            #     print(f'{i} pages', file=sys.stderr)

            page = msh.unmarshal(json.loads(l), mdl.Page)  # noqa

            verbose = False

            verbose and print(page.title)

            if page.revisions:
                rev = page.revisions[0]
                if rev.text:
                    # backend = mfh
                    backend = wtp0

                    if backend is mfh:
                        wiki = mfh.parse(rev.text.text)
                        # print(wiki)

                        wikilink: mfh.nodes.Wikilink
                        for wikilink in wiki.filter_wikilinks():  # noqa
                            verbose and print((wikilink.title, wikilink.text))

                        external_link: mfh.nodes.ExternalLink
                        for external_link in wiki.filter_external_links():  # noqa
                            verbose and print((external_link.title, external_link.url))

                    elif backend is wtp0:
                        parsed = wtp0.parse(rev.text.text)

                        for wikilink0 in parsed.wikilinks:
                            verbose and print((wikilink0.title, wikilink0.target))

                        for external_link0 in parsed.external_links:  # noqa
                            verbose and print((external_link0.text, external_link0.url))

                    else:
                        raise TypeError(backend)

                    buf = rev.text.text.encode('utf-8')
                    rb += len(buf)
                    cbuf = lz4.frame.compress(buf)
                    # cbuf = buf
                    cb += len(cbuf)

                    rows.append({
                        'id': page.id,
                        'title': page.title,
                        'text': cbuf,
                    })
                    maybe_flush_rows()

            verbose and print()

        maybe_flush_rows()


def _init_worker_proc():
    if sys.platform == 'linux':
        libc.prctl(libc.PR_SET_PDEATHSIG, signal.SIGTERM, 0, 0, 0, 0)


from multiprocessing.popen_spawn_posix import Popen as SpawnPosixPopen


class MySpawnPosixPopen(SpawnPosixPopen):
    def __init__(self, process_obj, *, extra_fds=None):
        self._extra_fds = extra_fds
        super().__init__(process_obj)

    def _launch(self, process_obj):
        if self._extra_fds:
            for fd in self._extra_fds:
                self.duplicate_for_child(fd)
            self._extra_fds = None
        super()._launch(process_obj)  # noqa


class MySpawnProcess(mp.context.SpawnProcess):
    def __init__(self, *args, extra_fds=None, **kwargs):
        self._extra_fds = extra_fds
        super().__init__(*args, **kwargs)

    def _Popen(self, process_obj):
        return MySpawnPosixPopen(process_obj, extra_fds=self._extra_fds)


class MySpawnContext(mp.context.SpawnContext):
    def __init__(self, extra_fds=None):
        super().__init__()
        self._extra_fds = extra_fds

    def Process(self, *args, **kwargs):  # noqa
        return MySpawnProcess(*args, extra_fds=self._extra_fds, **kwargs)


def _main() -> None:
    default_workers = 1

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-j', '--num-workers', type=int, default=default_workers)

    args = parser.parse_args()

    db_file = os.path.join('.data/wiki.db')
    if os.path.isfile(db_file):
        os.unlink(db_file)
    db_url = f'sqlite:///{db_file}'

    print(f'pid={os.getpid()}', file=sys.stderr)

    pr, pw = os.pipe()
    os.set_inheritable(pr, True)

    print(f'{pr=} {pw=}', file=sys.stderr)

    mp_context = MySpawnContext(extra_fds=[pr])

    with cfu.new_executor(
            args.num_workers,
            cf.ProcessPoolExecutor,
            initializer=_init_worker_proc,
            mp_context=mp_context,
    ) as ex:
        futs: list[cf.Future] = [
            ex.submit(
                analyze_file,
                db_url,
                fn,
                pr,
            )
            for fn in sorted(glob.glob(os.path.join(LZ4_JSONL_DIR, '*.jsonl.lz4')))
        ]
        for fut in futs:
            fut.result()


if __name__ == '__main__':
    _main()
