"""
bzip2 -cdk enwiki-20240801-pages-articles-multistream.xml.bz2 | lz4 -c > enwiki-20240801-pages-articles-multistream.xml.lz4

0 B / 42_781_970_578 B - 0.00 % - 0 B/s, 84404 elements, lang.is_gil_enabled()=False
"""  # noqa
import contextlib
import io
import os.path
import sys
import typing as ta

from omlish import lang
from omlish import marshal as msh
from omlish.formats import json

from . import models as mdl
from .utils import io as iou
from .utils import xml as xu
from .xml import parse_page


##


WIKI_REV = '20241101'


BZ2_INDEX_FILE_PATH = os.path.expanduser(f'~/data/enwiki/enwiki-{WIKI_REV}-pages-articles-multistream-index.txt.bz2')

#  23_851_879_117 compressed
# 103_090_295_026 uncompressed
BZ2_XML_FILE_PATH = os.path.expanduser(f'~/data/enwiki/enwiki-{WIKI_REV}-pages-articles-multistream.xml.bz2')

#  42_781_970_578 compressed
# 103_090_295_026 uncompressed
LZ4_XML_FILE_PATH = os.path.expanduser(f'~/data/enwiki/enwiki-{WIKI_REV}-pages-articles-multistream.xml.lz4')


def _main() -> None:
    # fp = BZ2_INDEX_FILE_PATH

    # fp = BZ2_XML_FILE_PATH
    fp = LZ4_XML_FILE_PATH

    use_subproc = False
    # use_subproc = True

    # use_lxml = False
    use_lxml = True

    output_dir = '.data/wiki/json'
    os.makedirs(output_dir, exist_ok=True)

    bs: ta.Any
    fpr: iou.FileProgressReporter | None
    with contextlib.ExitStack() as es:
        bs, fpr = es.enter_context(iou.open_compressed_reader(  # noqa
            fp,
            use_subprocess=use_subproc,
        ))

        mfw: iou.MultiFileWriter = es.enter_context(contextlib.closing(iou.MultiFileWriter(
            iou.Lz4MfwFile,
            os.path.join(output_dir, f'enwiki-{WIKI_REV}-pages-articles-%02d.jsonl.lz4'),
        )))

        if not use_lxml:
            cs = io.TextIOWrapper(bs, 'utf-8')
            it = xu.yield_root_children(cs)

        else:
            it = xu.yield_root_children(bs, use_lxml=True)

        root = next(it)  # noqa
        for i, el in enumerate(it):  # noqa
            if fpr is not None:
                if fpr.report():
                    print(f'{i} elements, {lang.is_gil_enabled()=}', file=sys.stderr)
            elif i and (i % 100_000) == 0:
                print(f'{i} elements, {lang.is_gil_enabled()=}', file=sys.stderr)

            if xu.strip_ns(el.tag) == 'page':
                page: mdl.Page = parse_page(el)

                oj = json.dumps_compact(msh.marshal(page))
                mfw.write(oj.encode('utf-8'), b'\n')


if __name__ == '__main__':
    _main()
