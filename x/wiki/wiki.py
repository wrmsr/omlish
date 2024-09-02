"""
https://www.mediawiki.org/wiki/Help:Export#Export_format

bzip2 -cdk enwiki-20240801-pages-articles-multistream.xml.bz2 | lz4 -c > enwiki-20240801-pages-articles-multistream.xml.lz4

0 B / 42_781_970_578 B - 0.00 % - 0 B/s, 84404 elements, lang.is_gil_enabled()=False
"""
import io  # noqa
import os.path
import subprocess  # noqa
import sys
import typing as ta

from . import xml
from .io import open_compressed
from .models import Page
from .models import SiteInfo
from .models import parse_page
from .models import parse_site_info

from omlish import lang  # noqa
from omlish import marshal as msh  # noqa
from omlish.formats import json  # noqa


##


BZ2_INDEX_FILE_PATH = os.path.expanduser('~/Downloads/enwiki-20240801-pages-articles-multistream-index.txt.bz2')

#  23_851_879_117 compressed
# 103_090_295_026 uncompressed
BZ2_XML_FILE_PATH = os.path.expanduser('~/Downloads/enwiki-20240801-pages-articles-multistream.xml.bz2')

#  42_781_970_578 compressed
# 103_090_295_026 uncompressed
LZ4_XML_FILE_PATH = os.path.expanduser('~/Downloads/enwiki-20240801-pages-articles-multistream.xml.lz4')


def _main() -> None:
    # print(os.getpid())
    # input()

    # fp = BZ2_INDEX_FILE_PATH

    # fp = BZ2_XML_FILE_PATH
    fp = LZ4_XML_FILE_PATH

    use_subproc = False
    # use_subproc = True

    # use_lxml = False
    use_lxml = True

    with open_compressed(
            fp,
            use_subprocess=use_subproc,
    ) as (bs, fpr):
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

            if xml.strip_ns(el.tag) == 'siteinfo':
                site_info = parse_site_info(el)

                print(site_info)
                oj = json.dumps_pretty(msh.marshal(site_info))
                print(oj)
                o2 = msh.unmarshal(json.loads(oj), SiteInfo)
                print(o2)

            elif xml.strip_ns(el.tag) == 'page':
                page = parse_page(el)

                print(page)
                oj = json.dumps_pretty(msh.marshal(page))
                print(oj)
                o2 = msh.unmarshal(json.loads(oj), Page)
                print(o2)

            # print(el)
            # print(list(root))
            # print()
            # input()


if __name__ == '__main__':
    _main()
