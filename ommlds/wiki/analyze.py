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
import argparse
import concurrent.futures as cf
import contextlib
import dataclasses as dc
import glob
import io
import os.path
import signal
import threading
import time
import typing as ta

import lz4.frame
import sqlalchemy as sa
import sqlalchemy.exc

from omlish import cached
from omlish import lang
from omlish import marshal as msh
from omlish import multiprocessing as mpu
from omlish.concurrent import all as conc
from omlish.formats import json
from omlish.logs import all as logs
from omlish.os import deathpacts

from . import models as mdl
from .text import mfh  # noqa
from .text import wtp  # noqa
from .utils.progress import ProgressReporter


log = logs.get_module_logger(globals())


##


LZ4_JSONL_DIR = os.path.expanduser('~/data/enwiki/json/')


meta = sa.MetaData()
pages_table = sa.Table(
    'pages',
    meta,
    sa.Column('id', sa.Integer(), primary_key=True),
    sa.Column('title', sa.String()),
    sa.Column('page', sa.BLOB),
    sa.Column('doc', sa.BLOB),
    sa.Index('pages_by_title', 'title'),
)


class FileAnalyzer:
    @dc.dataclass(frozen=True, kw_only=True)
    class Context:
        deathpact: deathpacts.Deathpact
        lock: threading.Lock
        num_rows: mpu.ValueProxy[int]

    def __init__(
        self,
        db_url: str,
        ctx: Context,
    ) -> None:
        super().__init__()

        self._db_url = db_url
        self._ctx = ctx

        self._es = contextlib.ExitStack()

        self._num_rows = 0
        self._rows: list[dict] = []

    #

    def __enter__(self) -> ta.Self:
        self._es.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self._es.__exit__(exc_type, exc_val, exc_tb)

    #

    @cached.function
    def _db(self) -> sa.Engine:
        db = sa.create_engine(self._db_url)
        self._es.enter_context(lang.defer(db.dispose))  # noqa
        return db

    def _setup_db(self) -> None:
        with self._ctx.lock:
            with self._db().begin() as conn:
                meta.create_all(bind=conn)

    #

    def _flush_rows(self) -> None:
        with self._ctx.lock:
            while True:
                try:
                    with self._db().begin() as conn:
                        conn.execute(pages_table.insert(), self._rows)

                except sa.exc.OperationalError as oe:
                    if 'database is locked' in repr(oe):  # FIXME: lol
                        log.warning(f'database is locked!!')  # noqa
                        time.sleep(1.)
                        continue
                    raise

                else:
                    break

            self._ctx.num_rows.set(self._ctx.num_rows.get() + len(self._rows))
            log.info(
                f'{len(self._rows):_} rows batched, '  # noqa
                f'{self._num_rows:_} rows file, '  # noqa
                f'{self._ctx.num_rows.get():_} rows total'  # noqa
            )

            self._rows.clear()

    row_batch_size = 1_000

    def _maybe_flush_rows(self):
        if len(self._rows) >= self.row_batch_size:
            self._flush_rows()

    #

    verbose = False

    parse_backend: ta.Any = (
        mfh
        # wtp
    )

    def _handle_line(self, l: str) -> bool:
        page = msh.unmarshal(json.loads(l), mdl.Page)  # noqa

        self.verbose and print(page.title)

        if not page.revisions:
            self.verbose and print()
            return False

        rev = page.revisions[0]

        if len(page.revisions) > 1:
            raise Exception(f'Multiple revisions: {page.id=} {page.title=}')

        if not (rev.text and rev.text.text):
            self.verbose and print()
            return False

        page_buf = json.dumps_compact(msh.marshal(page)).encode('utf-8')
        page_compressed_buf = lz4.frame.compress(page_buf)

        row = dict(
            id=page.id,
            title=page.title,
            page=page_compressed_buf,
        )

        if self.parse_backend is mfh:
            doc = mfh.parse_doc(rev.text.text)  # noqa
            # print(doc)

            doc_buf = json.dumps_compact(msh.marshal(doc, mfh.Doc)).encode('utf-8')
            doc_compressed_buf = lz4.frame.compress(doc_buf)

            row.update(
                doc=doc_compressed_buf,
            )

        elif self.parse_backend is wtp:
            tree = wtp.parse_tree(rev.text.text)  # noqa
            # print(tree)

        else:
            raise TypeError(self.parse_backend)

        self._rows.append(row)

        self.verbose and print()
        return True

    @logs.exception_logging(log)
    def run(self, file_name: str) -> None:
        log.info(f'{self._ctx.deathpact=} {file_name}')  # noqa

        self._setup_db()

        with contextlib.ExitStack() as es:
            f = es.enter_context(open(file_name, 'rb'))
            # fpr = iou.FileProgressReporter(f, time_interval=5)

            # proc = subprocess.Popen(['lz4', '-cdk', fn], stdout=subprocess.PIPE)
            # f = proc.stdout
            # fpr = None

            zf = es.enter_context(lz4.frame.open(f))
            tw = io.TextIOWrapper(zf, 'utf-8')

            file_pr = ProgressReporter[int](
                fn=f.tell,
                total=os.fstat(f.fileno()).st_size,
                fmt='_',
                suffix='B',
                report_interval=1_000_000,
            )
            rows_pr = ProgressReporter[int](
                start=self._num_rows,
                fmt='_',
                suffix='pages',
            )

            while (l := tw.readline()):
                self._num_rows += 1

                self._ctx.deathpact.poll()

                file_pr.update()
                rows_pr.update(self._num_rows)
                if file_pr.should_report or rows_pr.should_report:
                    log.info(
                        f'{os.path.basename(file_name)}: ' +  # noqa
                        ', '.join([
                            *file_pr.report(),
                            *rows_pr.report(),
                        ]),
                    )

                # if fpr is not None and fpr.report():  # noqa
                #     print(f'{i} pages', file=sys.stderr)

                if self._handle_line(l):
                    self._maybe_flush_rows()

            self._flush_rows()


@logs.exception_logging(log)
def analyze_file(
        file_name: str,
        db_url: str,
        ctx: FileAnalyzer.Context,
) -> None:
    FileAnalyzer(db_url, ctx).run(file_name)


##


def _init_process() -> None:
    logs.configure_standard_logging('INFO')


def _main() -> None:
    logs.configure_standard_logging('INFO')

    default_workers = 2

    #

    parser = argparse.ArgumentParser()
    parser.add_argument('-j', '--num-workers', type=int, default=default_workers)
    args = parser.parse_args()

    #

    db_file = os.path.join('.data/wiki.db')
    if os.path.isfile(db_file):
        os.unlink(db_file)
    db_url = f'sqlite:///{db_file}'

    log.info('Launching')  # noqa

    #

    with contextlib.ExitStack() as es:
        if default_workers:
            deathpact: deathpacts.PipeDeathpact = es.enter_context(deathpacts.PipeDeathpact())

            mp_context = mpu.ExtrasSpawnContext(mpu.SpawnExtras(
                pass_fds={deathpact.pass_fd},
                deathsig=signal.SIGTERM,
            ))

            mp_manager = mp_context.Manager()

            ctx = FileAnalyzer.Context(
                deathpact=deathpact,
                lock=mp_manager.Lock(),
                num_rows=mp_manager.Value('i', 0),
            )

            ex = es.enter_context(conc.new_executor(  # noqa
                args.num_workers,
                cf.ProcessPoolExecutor,
                mp_context=mp_context,
                initializer=_init_process,
            ))

        else:
            ctx = FileAnalyzer.Context(
                deathpact=deathpacts.NopDeathpact(),
                lock=threading.RLock(),  # type: ignore
                num_rows=mpu.DummyValueProxy(0),
            )

            ex = es.enter_context(conc.ImmediateExecutor())

        futs: list[cf.Future] = [
            ex.submit(
                analyze_file,
                file_name,
                db_url,
                ctx,
            )
            for file_name in sorted(
                glob.glob(os.path.join(LZ4_JSONL_DIR, '*.jsonl.lz4')),
                key=lambda fn: -os.stat(fn).st_size,
            )
        ]

        for fut in cf.as_completed(futs):
            try:
                fut.result()
            except Exception as e:  # noqa
                log.exception('Master caught exception')
                ex.shutdown(wait=False, cancel_futures=True)
                raise

        log.info(f'Complete! {ctx.num_rows.get()} rows total')  # noqa


if __name__ == '__main__':
    _main()
