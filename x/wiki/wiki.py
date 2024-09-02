"""
https://www.mediawiki.org/wiki/Help:Export#Export_format

https://github.com/5j9/wikitextparser
https://github.com/tatuylonen/wikitextprocessor
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
import lz4.frame

from . import models as mdl
from . import xml
from .io import open_compressed_reader


##


BZ2_INDEX_FILE_PATH = os.path.expanduser('~/Downloads/enwiki-20240801-pages-articles-multistream-index.txt.bz2')

#  23_851_879_117 compressed
# 103_090_295_026 uncompressed
BZ2_XML_FILE_PATH = os.path.expanduser('~/Downloads/enwiki-20240801-pages-articles-multistream.xml.bz2')

#  42_781_970_578 compressed
# 103_090_295_026 uncompressed
LZ4_XML_FILE_PATH = os.path.expanduser('~/Downloads/enwiki-20240801-pages-articles-multistream.xml.lz4')


class MultiFileWriter:
    def __init__(
            self,
            file_pat: str,
            file_size: int = 2 * 1024 * 1024 * 1024,
            *,
            use_compressed_size: bool = False,
    ) -> None:
        super().__init__()

        self._file_pat = file_pat
        self._file_size = file_size
        self._use_compressed_size = use_compressed_size

        self._n = 0
        self._b = 0
        self._raw_f: ta.IO | None = None
        self._z_f: ta.IO | None = None

    def close(self) -> None:
        if self._z_f is not None:
            self._z_f.close()
            self._z_f = None

        if self._raw_f is not None:
            self._raw_f.close()
            self._raw_f = None

    def write(self, *bufs: bytes) -> None:
        if self._raw_f is None:
            self._raw_f = open(self._file_pat % (self._n,), 'wb')
            self._z_f = lz4.frame.open(self._raw_f, 'wb')

        for buf in bufs:
            self._b += len(buf)
            self._z_f.write(buf)

        if (self._raw_f.tell() if self._use_compressed_size else self._b)  >= self._file_size:
            self.close()
            self._n += 1


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
        bs, fpr = es.enter_context(open_compressed_reader(  # noqa
            fp,
            use_subprocess=use_subproc,
        ))

        mfw: MultiFileWriter = es.enter_context(contextlib.closing(MultiFileWriter(
            os.path.join(output_dir, 'enwiki-20240801-pages-articles-%d.jsonl.lz4'),
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
