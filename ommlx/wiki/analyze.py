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
from omlish import marshal as msh
from omlish import multiprocessing as mpu
from omlish.formats import json

from . import models as mdl
from .utils.progress import ProgressReporter


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


def analyze_file(db_url: str, fn: str, dp: mpu.Deathpact) -> None:
    print(f'pid={os.getpid()} {dp=} {fn}', file=sys.stderr)

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


##


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

    with contextlib.ExitStack() as es:
        pdp: mpu.PipeDeathpact = es.enter_context(mpu.PipeDeathpact())

        mp_context = mpu.ExtrasSpawnContext(mpu.SpawnExtras(
            fds={pdp.fd},
            deathsig=signal.SIGTERM,
        ))

        ex = es.enter_context(cfu.new_executor(  # noqa
            args.num_workers,
            cf.ProcessPoolExecutor,
            mp_context=mp_context,
        ))

        futs: list[cf.Future] = [
            ex.submit(
                analyze_file,
                db_url,
                fn,
                pdp,
            )
            for fn in sorted(glob.glob(os.path.join(LZ4_JSONL_DIR, '*.jsonl.lz4')))
        ]
        for fut in futs:
            fut.result()


if __name__ == '__main__':
    _main()
