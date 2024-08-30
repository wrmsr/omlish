import typing as ta
import xml.etree.ElementTree


def strip_ns(tag: str) -> str:
    # It really do just be like this:
    # https://github.com/python/cpython/blob/ff3bc82f7c9882c27aad597aac79355da7257186/Lib/xml/etree/ElementTree.py#L803-L804
    if tag[:1] == '{':
        _, tag = tag[1:].rsplit('}', 1)
    return tag


ITER_PARSE_EVENTS = ('start', 'end', 'comment', 'pi', 'start-ns', 'end-ns')


def yield_root_children(source, *, retain_on_root: bool = False) -> ta.Iterator[xml.etree.ElementTree.Element]:
    it = iter(xml.etree.ElementTree.iterparse(source, ('start', 'end')))
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
