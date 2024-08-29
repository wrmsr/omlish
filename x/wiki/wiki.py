"""
https://www.mediawiki.org/wiki/Help:Export#Export_format
"""

"""
<mediawiki xml:lang="en">
  <page>
    <title>Page title</title>
    <restrictions>edit=sysop:move=sysop</restrictions>
    <revision>
      <timestamp>2001-01-15T13:15:00Z</timestamp>
      <contributor><username>Foobar</username></contributor>
      <comment>I have just one thing to say!</comment>
      <text>A bunch of [[Special:MyLanguage/text|text]] here.</text>
      <minor />
    </revision>
    <revision>
      <timestamp>2001-01-15T13:10:27Z</timestamp>
      <contributor><ip>10.0.0.2</ip></contributor>
      <comment>new!</comment>
      <text>An earlier [[Special:MyLanguage/revision|revision]].</text>
    </revision>
  </page>
  
  <page>
    <title>Talk:Page title</title>
    <revision>
      <timestamp>2001-01-15T14:03:00Z</timestamp>
      <contributor><ip>10.0.0.2</ip></contributor>
      <comment>hey</comment>
      <text>WHYD YOU LOCK PAGE??!!! i was editing that jerk</text>
    </revision>
  </page>
</mediawiki>
"""

"""
<!ELEMENT mediawiki (siteinfo,page*)>
<!-- version contains the version number of the format (currently 0.3) -->
<!ATTLIST mediawiki
  version  CDATA  #REQUIRED 
  xmlns CDATA #FIXED "https://www.mediawiki.org/xml/export-0.3/"
  xmlns:xsi CDATA #FIXED "http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation CDATA #FIXED
    "https://www.mediawiki.org/xml/export-0.3/ https://www.mediawiki.org/xml/export-0.3.xsd"
  xml:lang  CDATA #IMPLIED
>
<!ELEMENT siteinfo (sitename,base,generator,case,namespaces)>
<!ELEMENT sitename (#PCDATA)>      <!-- Name of the wiki -->
<!ELEMENT base (#PCDATA)>          <!-- URL of the main page -->
<!ELEMENT generator (#PCDATA)>     <!-- MediaWiki version string -->
<!ELEMENT case (#PCDATA)>          <!-- How cases in page names are handled -->
   <!-- possible values: 'first-letter' | 'case-sensitive'
        'Case-insensitive' option is reserved for future -->
<!ELEMENT namespaces (namespace+)> <!-- List of namespaces and prefixes -->
  <!ELEMENT namespace (#PCDATA)>     <!-- Contains namespace prefix -->
  <!ATTLIST namespace key CDATA #REQUIRED> <!-- Internal namespace number -->
<!ELEMENT page (title,id?,restrictions?,(revision|upload)*)>
  <!ELEMENT title (#PCDATA)>         <!-- Title with namespace prefix -->
  <!ELEMENT id (#PCDATA)> 
  <!ELEMENT restrictions (#PCDATA)>  <!-- Optional page restrictions -->
<!ELEMENT revision (id?,timestamp,contributor,minor?,comment?,text)>
  <!ELEMENT timestamp (#PCDATA)>     <!-- According to ISO8601 -->
  <!ELEMENT minor EMPTY>             <!-- Minor flag -->
  <!ELEMENT comment (#PCDATA)> 
  <!ELEMENT text (#PCDATA)>          <!-- Wikisyntax -->
  <!ATTLIST text xml:space CDATA  #FIXED "preserve">
<!ELEMENT contributor ((username,id) | ip)>
  <!ELEMENT username (#PCDATA)>
  <!ELEMENT ip (#PCDATA)>
<!ELEMENT upload (timestamp,contributor,comment?,filename,src,size)>
  <!ELEMENT filename (#PCDATA)>
  <!ELEMENT src (#PCDATA)>
  <!ELEMENT size (#PCDATA)>
"""

import abc
import bz2
import dataclasses as dc
import io
import os.path
import subprocess
import time
import typing as ta
import xml.etree.ElementTree

from omlish import check


def cut_chunks(
        chunks: ta.Iterable[str],
        sep: str = os.linesep,
        *,
        max_buf_size=10 * 1024 * 1024,
        buf_cls=io.StringIO,
):
    buf = buf_cls()

    for chunk in chunks:
        if sep not in chunk:
            buf.write(chunk)
        else:
            line_chunks = chunk.split(sep)
            buf.write(line_chunks[0])
            yield buf.getvalue()
            if buf.tell() > max_buf_size:
                buf.close()
                buf = buf_cls()
            else:
                buf.seek(0, 0)
                buf.truncate()
            if len(line_chunks) > 1:
                for i in range(1, len(line_chunks) - 1):
                    yield line_chunks[i]
                buf.write(line_chunks[-1])

    if buf.tell() > 0:
        yield buf.getvalue()


class BytesReaderWrapper(ta.IO[bytes], abc.ABC):
    def __init__(self, f: ta.IO[bytes]) -> None:
        super().__init__()
        self._f = f

    def close(self):
        raise TypeError

    def fileno(self):
        return self._f.fileno()

    def flush(self):
        raise TypeError

    def isatty(self):
        return self._f.isatty()

    @abc.abstractmethod
    def read(self, n=-1):
        raise NotImplementedError

    def readable(self):
        return self._f.readable()

    def readline(self, limit=-1):
        raise TypeError

    def readlines(self, hint=-1):
        raise TypeError

    def seek(self, offset, whence=0):
        raise TypeError

    def seekable(self):
        return False

    def tell(self):
        return self._f.tell()

    def truncate(self, size=None):
        raise TypeError

    def writable(self):
        return self._f.writable()

    def write(self, s):
        raise TypeError

    def writelines(self, lines):
        raise TypeError

    def __next__(self):
        raise TypeError

    def __iter__(self):
        raise TypeError

    def __enter__(self):
        raise TypeError

    def __exit__(self, et, e, tb):
        raise TypeError


class Bz2ReaderWrapper(BytesReaderWrapper):
    """
    TODO:
     - parallel decompress
    """

    def __init__(self, f: ta.IO[bytes]) -> None:
        super().__init__(f)
        self._b = bz2.BZ2Decompressor()
        self._c = 0
        self._e = False
        self._x: bytes | None = None

    def read(self, n=-1):
        while True:
            if self._e or not (r := self._f.read(n)):
                self._e = True

                if self._x:
                    r = self._x
                    self._x = None
                    return r

                if self._c and not self._b.eof:
                    raise Exception('not at eof')

                return b''

            self._c += len(r)
            ret = self._b.decompress(r)
            if self._x:
                ret = self._x + ret
                self._x = None

            if self._b.eof:
                u = self._b.unused_data
                self._b = bz2.BZ2Decompressor()
                self._c = 0
                if u:
                    self._x = self._b.decompress(u)

            if ret:
                return ret


def _stream_decompress(fp: str) -> None:
    fst = os.stat(fp)
    with open(fp, 'rb') as f:
        br = io.BufferedReader(f, 1024 * 1024)
        bs = Bz2ReaderWrapper(br)
        cs = io.TextIOWrapper(bs, 'utf-8')

        # while (chunk := cs.read(1024)):
        #     # print(chunk)
        #     pass

        lp = 0
        st = time.time()
        pi = 10_000_000
        while (line := cs.readline()):
            cp = f.tell()
            if cp - lp >= pi:
                ct = time.time()
                nr = cp - lp
                et = ct - st
                print(
                    f'{cp:_} b / {fst.st_size:_} b - '
                    f'{cp / fst.st_size * 100.:.2f} % - '
                    f'{int(nr / et):_} b/s'
                )
                lp = cp
                st = ct

            # print(line.strip())


##


INDEX_FILE_PATH = os.path.expanduser('~/Downloads/enwiki-20240801-pages-articles-multistream-index.txt.bz2')
XML_FILE_PATH = os.path.expanduser('~/Downloads/enwiki-20240801-pages-articles-multistream.xml.bz2')


@dc.dataclass(frozen=True)
class SiteInfo:
    sitename: str | None = None
    base: str | None = None
    generator: str | None = None
    case: str | None = None
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
    revisions: ta.Optional['Revision'] = None


@dc.dataclass(frozen=True)
class Redirect:
    title: str | None = None  # att


@dc.dataclass(frozen=True)
class Revision:
    id: str | None = None
    parentid: str | None = None
    timestamp: str | None = None
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


#


def _main() -> None:
    # print(os.getpid())
    # input()

    # fp = INDEX_FILE_PATH
    fp = XML_FILE_PATH

    proc = subprocess.Popen(['pbzip2', '-cdk', fp], stdout=subprocess.PIPE)

    # for c in iter(lambda: proc.stdout.read(1024 * 1024), b''):
    #     print(c)

    tag_stack = []
    kw_stack = []

    # "start", "end", "comment", "pi", "start-ns", "end-ns"
    for ev, el in xml.etree.ElementTree.iterparse(proc.stdout, ('start', 'end')):
        if ev == 'start':
            tag = el.tag
            # It really do just be like this:
            # https://github.com/python/cpython/blob/ff3bc82f7c9882c27aad597aac79355da7257186/Lib/xml/etree/ElementTree.py#L803-L804
            if tag[:1] == '{':
                _, tag = tag[1:].rsplit('}', 1)

            if not tag_stack:
                if tag != 'mediawiki':
                    raise RuntimeError('unexpected root tag')

            else:
                kw_stack.append({})

            tag_stack.append(tag)

        elif ev == 'end':
            tag_stack.pop()

        print((ev, el, tag_stack))


if __name__ == '__main__':
    _main()
