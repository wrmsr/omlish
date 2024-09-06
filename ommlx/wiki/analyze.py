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
import glob
import io
import logging
import multiprocessing as mp
import multiprocessing.managers
import os.path
import signal
import threading

import lz4.frame
import sqlalchemy as sa

from omlish import concurrent as cfu
from omlish import lang
from omlish import logs
from omlish import marshal as msh
from omlish import multiprocessing as mpu
from omlish.formats import json

from . import models as mdl
from .text import mfh
from .text import wtp
from .utils.progress import ProgressReporter


log = logging.getLogger(__name__)


##


LZ4_JSONL_DIR = os.path.expanduser('~/data/enwiki/json/')


meta = sa.MetaData()
pages_table = sa.Table(
    'pages',
    meta,
    sa.Column('id', sa.Integer(), primary_key=True),
    sa.Column('title', sa.String()),
    sa.Column('text', sa.BLOB),
)


@logs.error_logging(log)
def analyze_file(
        db_url: str,
        fn: str,
        dp: mpu.Deathpact,
        lck: threading.Lock,
        nr: mp.managers.ValueProxy,
) -> None:
    log.info(f'pid={os.getpid()} {dp=} {fn}')  # noqa

    rows: list[dict] = []
    row_batch_size = 1_000

    rb = 0
    cb = 0

    efn = os.path.basename(fn)

    with contextlib.ExitStack() as es:
        engine = sa.create_engine(db_url)
        es.enter_context(lang.defer(engine.dispose))  # noqa

        with lck:
            with engine.begin() as conn:
                meta.create_all(bind=conn)

        def maybe_flush_rows():
            if len(rows) >= row_batch_size:
                with lck:
                    with engine.begin() as conn:
                        conn.execute(pages_table.insert(), rows)

                    nr.value += len(rows)
                    log.info(f'{efn}: {len(rows)} rows batched, {i} rows file, {nr.value} rows total')  # noqa

                rows.clear()

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

            dp.poll()

            fpr0.update()
            fpr1.update(i)
            if fpr0.should_report or fpr1.should_report:
                log.info(f'{efn}: ' + ', '.join([*fpr0.report(), *fpr1.report()]))  # noqa
                log.info(f'{efn}: {rb:_} B raw, {cb:_} B cpr, {cb / rb * 100.:.02f} %')  # noqa
                rb = cb = 0

            # if fpr is not None and fpr.report():  # noqa
            #     print(f'{i} pages', file=sys.stderr)

            page = msh.unmarshal(json.loads(l), mdl.Page)  # noqa

            verbose = False

            verbose and print(page.title)

            if page.revisions:
                rev = page.revisions[0]

                # if len(page.revisions) > 1:
                #     breakpoint()

                if rev.text and rev.text.text:
                    # backend = mfh
                    backend = wtp

                    if backend is mfh:
                        dom = mfh.parse_nodes(rev.text.text)  # noqa
                        # print(dom)

                    elif backend is wtp:
                        tree = wtp.parse_tree(rev.text.text)  # noqa
                        # print(tree)

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


##


def _init_process() -> None:
    logs.configure_standard_logging('INFO')


def _main() -> None:
    logs.configure_standard_logging('INFO')

    default_workers = 0

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-j', '--num-workers', type=int, default=default_workers)

    args = parser.parse_args()

    db_file = os.path.join('.data/wiki.db')
    if os.path.isfile(db_file):
        os.unlink(db_file)
    db_url = f'sqlite:///{db_file}'

    log.info(f'pid={os.getpid()}')  # noqa

    with contextlib.ExitStack() as es:
        pdp: mpu.PipeDeathpact = es.enter_context(mpu.PipeDeathpact())

        mp_context = mpu.ExtrasSpawnContext(mpu.SpawnExtras(
            fds={pdp.pass_fd},
            deathsig=signal.SIGTERM,
        ))

        mgr = mp_context.Manager()

        ex = es.enter_context(cfu.new_executor(  # noqa
            args.num_workers,
            cf.ProcessPoolExecutor,
            mp_context=mp_context,
            initializer=_init_process,
        ))

        nr = mgr.Value('i', 0)

        futs: list[cf.Future] = [
            ex.submit(
                analyze_file,
                db_url,
                fn,
                pdp,
                mgr.Lock(),
                nr,
            )
            for fn in sorted(
                glob.glob(os.path.join(LZ4_JSONL_DIR, '*.jsonl.lz4')),
                key=lambda fn: -os.stat(fn).st_size,
            )
        ]
        for fut in futs:
            fut.result()

        log.info(f'{nr.value} rows total')  # noqa


if __name__ == '__main__':
    _main()
