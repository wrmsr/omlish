"""
https://www.mediawiki.org/wiki/Help:Export#Export_format

bzip2 -cdk enwiki-20240801-pages-articles-multistream.xml.bz2 | lz4 -c > enwiki-20240801-pages-articles-multistream.xml.lz4
"""
import contextlib
import dataclasses as dc
import os.path
import io  # noqa
import subprocess  # noqa
import typing as ta

from .io import Bz2ReaderWrapper  # noqa
from .io import FileProgressReporter  # noqa
from .xml import strip_ns  # noqa
from .xml import yield_root_children


##


@dc.dataclass(frozen=True)
class MediaWiki:
    siteinfo: ta.Optional['SiteInfo'] = None
    pages: ta.Sequence['Page'] = None


@dc.dataclass(frozen=True)
class SiteInfo:
    sitename: str | None = None
    base: str | None = None
    generator: str | None = None
    case: str | None = None  # 'first-letter' | 'case-sensitive'
    namespaces: ta.Sequence['Namespace'] | None = None


@dc.dataclass(frozen=True)
class Namespace:
    key: str | None = None  # att
    case: str | None = None  # att
    text: str | None = None  # text


@dc.dataclass(frozen=True)
class Page:
    title: str | None = None
    ns: str | None = None
    id: str | None = None
    redirect: ta.Optional['Redirect'] = None
    restrictions: str | None = None
    revisions: ta.Optional[ta.Sequence['Revision']] = None
    uploads: ta.Optional[ta.Sequence['Upload']] = None


@dc.dataclass(frozen=True)
class Redirect:
    title: str | None = None  # att


@dc.dataclass(frozen=True)
class Revision:
    id: str | None = None
    parentid: str | None = None
    timestamp: str | None = None  # ISO8601
    contributors: ta.Sequence['Contributor'] | None = None
    minor: bool = False
    comment: str | None = None
    origin: str | None = None
    model: str | None = None
    format: str | None = None
    text: ta.Optional['RevisionText'] = None
    sha1: str | None = None


@dc.dataclass(frozen=True)
class Contributor:
    username: str | None = None
    ip: str | None = None


@dc.dataclass(frozen=True)
class RevisionText:
    bytes: str | None = None  # att
    sha1: str | None = None  # att
    text: str | None = None  # text


@dc.dataclass(frozen=True)
class Upload:
    timestamp: str | None = None
    contributor: str | None = None
    comment: str | None = None
    filename: str | None = None
    src: str | None = None
    size: str | None = None


##


BZ2_INDEX_FILE_PATH = os.path.expanduser('~/Downloads/enwiki-20240801-pages-articles-multistream-index.txt.bz2')

#  23_851_879_117 compressed
# 103_090_295_026 uncompressed
BZ2_XML_FILE_PATH = os.path.expanduser('~/Downloads/enwiki-20240801-pages-articles-multistream.xml.bz2')


def _main() -> None:
    # print(os.getpid())
    # input()

    # fp = INDEX_FILE_PATH
    fp = BZ2_XML_FILE_PATH

    use_subproc = False
    # use_subproc = True

    # use_lxml = False
    use_lxml = True

    with contextlib.ExitStack() as es:
        if not use_subproc:
            f = es.enter_context(open(fp, 'rb'))
            fpr = FileProgressReporter(f, time_interval=5)
            br = io.BufferedReader(f, 1024 * 1024)
            bs = Bz2ReaderWrapper(br)

        else:
            # proc = subprocess.Popen(['pbzip2', '-cdk', fp], stdout=subprocess.PIPE)
            proc = subprocess.Popen(['bzip2', '-cdk', fp], stdout=subprocess.PIPE)
            bs = proc.stdout
            fpr = None

        if not use_lxml:
            cs = io.TextIOWrapper(bs, 'utf-8')
            it = yield_root_children(cs)

        else:
            it = yield_root_children(bs, use_lxml=True)

        root = next(it)  # noqa
        for el in it:  # noqa
            if fpr is not None:
                fpr.report()

            # print(el)
            # print(list(root))
            # print()
            # input()


if __name__ == '__main__':
    _main()
