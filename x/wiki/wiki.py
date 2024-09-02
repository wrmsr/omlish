"""
https://www.mediawiki.org/wiki/Help:Export#Export_format

https://github.com/5j9/wikitextparser
https://github.com/tatuylonen/wikitextprocessor
https://github.com/earwig/mwparserfromhell

https://github.com/WillKoehrsen/wikipedia-data-science/blob/master/notebooks/Downloading%20and%20Parsing%20Wikipedia%20Articles.ipynb

https://en.wikipedia.org/wiki/Help:Wikitext
https://en.wikipedia.org/wiki/Wikipedia:Lua

bzip2 -cdk enwiki-20240801-pages-articles-multistream.xml.bz2 | lz4 -c > enwiki-20240801-pages-articles-multistream.xml.lz4

0 B / 42_781_970_578 B - 0.00 % - 0 B/s, 84404 elements, lang.is_gil_enabled()=False

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
import io  # noqa
import os.path
import subprocess  # noqa
import sys
import typing as ta

from omlish import lang  # noqa
from omlish import marshal as msh  # noqa
from omlish.formats import json  # noqa

from . import io as iou
from . import models as mdl
from . import xml


##


BZ2_INDEX_FILE_PATH = os.path.expanduser('~/Downloads/enwiki-20240801-pages-articles-multistream-index.txt.bz2')

#  23_851_879_117 compressed
# 103_090_295_026 uncompressed
BZ2_XML_FILE_PATH = os.path.expanduser('~/Downloads/enwiki-20240801-pages-articles-multistream.xml.bz2')

#  42_781_970_578 compressed
# 103_090_295_026 uncompressed
LZ4_XML_FILE_PATH = os.path.expanduser('~/Downloads/enwiki-20240801-pages-articles-multistream.xml.lz4')


def _main() -> None:
    # fp = BZ2_INDEX_FILE_PATH

    # fp = BZ2_XML_FILE_PATH
    fp = LZ4_XML_FILE_PATH

    use_subproc = False
    # use_subproc = True

    # use_lxml = False
    use_lxml = True

    output_dir = os.path.join(os.path.dirname(__file__), 'out')
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    with contextlib.ExitStack() as es:
        bs, fpr = es.enter_context(iou.open_compressed_reader(  # noqa
            fp,
            use_subprocess=use_subproc,
        ))

        mfw: iou.MultiFileWriter = es.enter_context(contextlib.closing(iou.MultiFileWriter(
            iou.Lz4MfwFile,
            os.path.join(output_dir, 'enwiki-20240801-pages-articles-%02d.jsonl.lz4'),
        )))

        if not use_lxml:
            cs = io.TextIOWrapper(bs, 'utf-8')
            it = xml.yield_root_children(cs)

        else:
            it = xml.yield_root_children(bs, use_lxml=True)

        root = next(it)  # noqa
        for i, el in enumerate(it):  # noqa
            if fpr is not None:
                if fpr.report():
                    print(f'{i} elements, {lang.is_gil_enabled()=}', file=sys.stderr)
            elif i and (i % 100_000) == 0:
                print(f'{i} elements, {lang.is_gil_enabled()=}', file=sys.stderr)

            if xml.strip_ns(el.tag) == 'page':
                page: mdl.Page = mdl.parse_page(el)

                oj = json.dumps_compact(msh.marshal(page))
                mfw.write(oj.encode('utf-8'), b'\n')


if __name__ == '__main__':
    _main()
