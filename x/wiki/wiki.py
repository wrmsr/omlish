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

import contextlib
import dataclasses as dc
import os.path
import subprocess
import sys
import time
import typing as ta
import xml.etree.ElementTree

from .io import Bz2ReaderWrapper
from .xml import strip_ns
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



##


INDEX_FILE_PATH = os.path.expanduser('~/Downloads/enwiki-20240801-pages-articles-multistream-index.txt.bz2')
XML_FILE_PATH = os.path.expanduser('~/Downloads/enwiki-20240801-pages-articles-multistream.xml.bz2')


def _main() -> None:
    # print(os.getpid())
    # input()

    # fp = INDEX_FILE_PATH
    fp = XML_FILE_PATH

    # proc = subprocess.Popen(['pbzip2', '-cdk', fp], stdout=subprocess.PIPE)
    proc = subprocess.Popen(['bzip2', '-cdk', fp], stdout=subprocess.PIPE)

    # for c in iter(lambda: proc.stdout.read(1024 * 1024), b''):
    #     print(c)

    tag_stack = []
    el_stack = []
    # kw_stack = []

    # xml.etree.ElementTree.ParseError: no element found: line 32794611, column 0
    # xml.etree.ElementTree.ParseError: no element found: line 42182045, column 0

    with contextlib.ExitStack() as es:
        # f = es.enter_context(open(fp, 'rb'))
        # fpr = FileProgressReporter(f)
        # br = io.BufferedReader(f, 1024 * 1024)
        # bs = Bz2ReaderWrapper(br)
        # cs = io.TextIOWrapper(bs, 'utf-8')
        cs = proc.stdout

        it = yield_root_children(cs)
        root = next(it)
        for el in it:
            print(el)
            print(list(root))
            print()
            input()

        # "start", "end", "comment", "pi", "start-ns", "end-ns"
        for ev, el in xml.etree.ElementTree.iterparse(cs, ('start', 'pi', 'end')):
            if ev == 'start':
                tag = el.tag
                if not tag_stack:
                    if tag != 'mediawiki':
                        raise RuntimeError('unexpected root tag')

                # else:
                #     kw_stack.append({})

                el_stack.append(el)
                tag_stack.append(tag)

            elif ev == 'end':
                # kw_stack.pop()

                tag_stack.pop()
                el_stack.pop()

                # # https://stackoverflow.com/a/12161078
                # el.clear()
                #
                # # Also eliminate now-empty references from the root node to elem
                # for ancestor in el.xpath('ancestor-or-self::*'):
                #     while ancestor.getprevious() is not None:
                #         del ancestor.getparent()[0]

            # print((ev, el, tag_stack))


if __name__ == '__main__':
    _main()
