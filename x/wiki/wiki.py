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

import bz2
import io
import os.path
import typing as ta

from omlish import check


def cut_lines(
        chunks: ta.Iterable[str],
        max_buf_size=10 * 1024 * 1024,
        buf_cls=io.StringIO,
):
    buf = buf_cls()

    for chunk in chunks:
        if os.linesep not in chunk:
            buf.write(chunk)
        else:
            line_chunks = chunk.splitlines()
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


class ChunkMappingBytesReader(ta.IO[bytes]):
    def __init__(
            self,
            f: ta.IO[bytes],
            map_fn: ta.Callable[[bytes], bytes],
            end_fn: ta.Callable[[], None] | None = None,
    ) -> None:
        super().__init__()
        self._f = f
        self._map_fn = map_fn
        self._end_fn = end_fn

    def close(self):
        raise TypeError

    def fileno(self):
        return self._f.fileno()

    def flush(self):
        raise TypeError

    def isatty(self):
        return self._f.isatty()

    def read(self, n=-1):
        while True:
            if not (buf := self._f.read(n)):
                if self._end_fn is not None:
                    self._end_fn()
                return buf
            if (buf := self._map_fn(buf)):
                return buf

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


INDEX_FILE_PATH = os.path.expanduser('~/Downloads/enwiki-20240801-pages-articles-multistream-index.txt.bz2')
XML_FILE_PATH = os.path.expanduser('~/Downloads/enwiki-20240801-pages-articles-multistream.xml.bz2')


def _main() -> None:
    # print(os.getpid())
    # input()

    with open(INDEX_FILE_PATH, 'rb') as f:
        br = io.BufferedReader(f, 1024 * 1024)
        bs = ChunkMappingBytesReader(br, (bd := bz2.BZ2Decompressor()).decompress, lambda: check.state(bd.eof))
        cs = io.TextIOWrapper(bs, 'utf-8')

        # while (chunk := cs.read(1024)):
        #     # print(chunk)
        #     pass

        while (line := cs.readline()):
            pass


if __name__ == '__main__':
    _main()
