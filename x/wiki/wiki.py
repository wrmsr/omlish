"""
https://www.mediawiki.org/wiki/Help:Export#Export_format

bzip2 -cdk enwiki-20240801-pages-articles-multistream.xml.bz2 | lz4 -c > enwiki-20240801-pages-articles-multistream.xml.lz4

0 B / 42_781_970_578 B - 0.00 % - 0 B/s, 84404 elements, lang.is_gil_enabled()=False
"""
import contextlib
import dataclasses as dc
import io  # noqa
import os.path
import subprocess  # noqa
import sys
import typing as ta

from . import xml
from .io import FileProgressReporter  # noqa

from omlish import lang  # noqa
from omlish import marshal as msh  # noqa
from omlish.formats import json  # noqa


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
    id: str | None = None
    ip: str | None = None
    deleted: str | None = None


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


def parse_contributor(el: xml.Element) -> Contributor:
    kw = {}
    if el.attrib:
        for k, v in el.attrib.items():
            if k in ('deleted',):
                if k in kw:
                    raise KeyError(k)
                kw[k] = v
            else:
                raise KeyError(k)
    for cel in el:
        if (ctag := xml.strip_ns(cel.tag)) in ('username', 'id', 'ip'):
            if ctag in kw:
                raise KeyError(ctag)
            kw[ctag] = cel.text
        else:
            raise KeyError(ctag)
    return Contributor(**kw)


def parse_revision_text(el: xml.Element) -> RevisionText:
    kw = {}
    if el.attrib:
        for k, v in el.attrib.items():
            if k in ('bytes', 'sha1'):
                if k in kw:
                    raise KeyError(k)
                kw[k] = v
            elif xml.strip_ns(k) in ('space',):
                continue
            else:
                raise KeyError(k)
    kw['text'] = el.text
    for cel in el:
        raise KeyError(xml.strip_ns(cel.tag))
    return RevisionText(**kw)


def parse_revision(el: xml.Element) -> Revision:
    if el.attrib:
        raise KeyError
    kw = {}
    for cel in el:
        if (ctag := xml.strip_ns(cel.tag)) in ('id', 'parentid', 'timestamp', 'minor', 'comment', 'origin', 'model', 'format', 'sha1'):
            if ctag in kw:
                raise KeyError(ctag)
            kw[ctag] = cel.text
        elif ctag == 'contributor':
            if ctag in kw:
                raise KeyError(ctag)
            kw.setdefault('contributors', []).append(parse_contributor(cel))
        elif ctag == 'text':
            if ctag in kw:
                raise KeyError(ctag)
            kw[ctag] = parse_revision_text(cel)
        else:
            raise KeyError(ctag)
    return Revision(**kw)


def parse_redirect(el: xml.Element) -> Redirect:
    kw = {}
    if 'title' in el.attrib:
        kw['title'] = el.attrib['title']
    for cel in el:
        raise KeyError(xml.strip_ns(cel.tag))
    return Redirect(**kw)


def parse_page(el: xml.Element) -> Page:
    if el.attrib:
        raise KeyError
    kw = {}
    for cel in el:
        if (ctag := xml.strip_ns(cel.tag)) in ('title', 'ns', 'id', 'restrictions'):
            if ctag in kw:
                raise KeyError(ctag)
            kw[ctag] = cel.text
        elif ctag == 'redirect':
            if ctag in kw:
                raise KeyError(ctag)
            kw[ctag] = parse_redirect(cel)
        elif ctag == 'revision':
            kw.setdefault('revisions', []).append(parse_revision(cel))
        elif ctag == 'upload':
            raise NotImplementedError
        else:
            raise KeyError(ctag)
    return Page(**kw)


##


def xml_to_dataclass(
        el: xml.Element,
        attrs: ta.Sequence[str],
        scalars: ta.Sequence[str],
        single_children: ta.Sequence[str],
        list_children: ta.Sequence[tuple[str, str, ta.Callable[[xml.Element], ta.Any]]],
) -> ta.Any:
    raise NotImplementedError


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

    use_lxml = False
    # use_lxml = True

    with contextlib.ExitStack() as es:
        if fp.endswith('.bz2'):
            if not use_subproc:
                f = es.enter_context(open(fp, 'rb'))
                fpr = FileProgressReporter(f, time_interval=5)

                import bz2
                bs = es.enter_context(contextlib.closing(bz2.open(f, 'rb')))

            else:
                f = es.enter_context(open(fp, 'rb'))

                # FIXME: os.dup?
                # fpr = FileProgressReporter(f, time_interval=5)
                fpr = None

                # proc = subprocess.Popen(['pbzip2', '-cdk', fp], stdout=subprocess.PIPE)
                proc = subprocess.Popen(['bzip2', '-cdk', fp], stdout=subprocess.PIPE, stdin=f)
                bs = proc.stdout

        elif fp.endswith('.lz4'):
            if not use_subproc:
                f = es.enter_context(open(fp, 'rb'))
                fpr = FileProgressReporter(f, time_interval=5)

                import lz4.frame
                bs = es.enter_context(contextlib.closing(lz4.frame.open(f, 'rb')))

            else:
                f = es.enter_context(open(fp, 'rb'))

                # FIXME: os.dup?
                # fpr = FileProgressReporter(f, time_interval=5)
                fpr = None

                proc = subprocess.Popen(['lz4', '-cdk', fp], stdout=subprocess.PIPE, stdin=f)
                bs = proc.stdout

        else:
            raise RuntimeError(fp)

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
                page = parse_page(el)

                print(json.dumps_pretty(msh.marshal(page)))

            # print(el)
            # print(list(root))
            # print()
            # input()


if __name__ == '__main__':
    _main()
