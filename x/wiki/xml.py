"""
TODO:
 - lxml? faster?
  - https://lxml.de/1.3/compatibility.html
  - https://lxml.de/performance.html
 - https://docs.python.org/3/library/xml.etree.elementtree.html#xml.etree.ElementTree.XMLPullParser - sans-io
"""
import typing as ta
import xml.etree.ElementTree

from omlish import lang


if ta.TYPE_CHECKING:
    import lxml.etree as lxml_etree
else:
    lxml_etree = lang.proxy_import('lxml.etree')


def strip_ns(tag: str) -> str:
    # It really do just be like this:
    # https://github.com/python/cpython/blob/ff3bc82f7c9882c27aad597aac79355da7257186/Lib/xml/etree/ElementTree.py#L803-L804
    if tag[:1] == '{':
        _, tag = tag[1:].rsplit('}', 1)
    return tag


ITER_PARSE_EVENTS = ('start', 'end', 'comment', 'pi', 'start-ns', 'end-ns')


def yield_root_children(
        source: ta.Any,
        *,
        retain_on_root: bool = False,
        use_lxml: bool = False,
        **kwargs: ta.Any,
) -> ta.Iterator[xml.etree.ElementTree.Element]:
    if use_lxml:
        parser = lxml_etree.iterparse
    else:
        parser = xml.etree.ElementTree.iterparse
    it = iter(parser(source, ('start', 'end'), **kwargs))

    ev, root = next(it)
    if ev != 'start':
        raise RuntimeError(ev)
    yield root

    depth = 0
    for ev, el in it:
        if ev == 'start':
            depth += 1

        elif ev == 'end':
            depth -= 1
            if not depth:
                if not retain_on_root:
                    root.remove(el)
                yield el
