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
import sys

import lz4.frame
import mwparserfromhell as mfh
import mwparserfromhell.nodes  # noqa

from omlish import marshal as msh
from omlish.formats import json

from . import models as mdl
from .progress import ProgressReporter


LZ4_JSONL_DIR = os.path.expanduser('~/data/enwiki/json/')


def analyze_file(fn: str) -> None:
    print(f'pid={os.getpid()} {fn}')

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

            fpr0.update()
            fpr1.update(i)
            if fpr0.should_report or fpr1.should_report:
                print(', '.join([*fpr0.report(), *fpr1.report()]), file=sys.stderr)

            # if fpr is not None and fpr.report():  # noqa
            #     print(f'{i} pages', file=sys.stderr)

            page = msh.unmarshal(json.loads(l), mdl.Page)  # noqa

            # print(page.title)

            for rev in page.revisions or ():
                if rev.text:
                    wiki = mfh.parse(rev.text.text)
                    # print(wiki)

                    wikilink: mfh.nodes.Wikilink
                    for wikilink in wiki.filter_wikilinks():  # noqa
                        # print((wikilink.title, wikilink.text))
                        pass

                    external_link: mfh.nodes.ExternalLink
                    for external_link in wiki.filter_external_links():  # noqa
                        # print((external_link.title, external_link.url))
                        pass

            # print()


def _main() -> None:
    with cf.ProcessPoolExecutor(8) as ex:
        futs: list[cf.Future] = [
            ex.submit(
                analyze_file,
                fn,
            )
            for fn in glob.glob(os.path.join(LZ4_JSONL_DIR, '*.jsonl.lz4'))
        ]
        for fut in futs:
            fut.result()


if __name__ == '__main__':
    _main()
