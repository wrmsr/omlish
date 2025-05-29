"""
TODO:
 - lxml abstraction
 - stuff from ommlds/wiki
"""
import typing as ta

from .. import cached
from .. import dataclasses as dc
from .. import lang


if ta.TYPE_CHECKING:
    import xml.etree.ElementTree as ET
else:
    ET = lang.proxy_import('xml.etree.ElementTree')


##


def strip_ns(tag: str) -> str:
    # It really do just be like this:
    # https://github.com/python/cpython/blob/ff3bc82f7c9882c27aad597aac79355da7257186/Lib/xml/etree/ElementTree.py#L803-L804
    if tag[:1] == '{':
        _, tag = tag[1:].rsplit('}', 1)
    return tag


##


ITER_PARSE_EVENTS = ('start', 'end', 'comment', 'pi', 'start-ns', 'end-ns')


def yield_root_children(
        source: ta.Any,
        *,
        retain_on_root: bool = False,
        **kwargs: ta.Any,
) -> ta.Iterator['ET.Element']:
    it = iter(ET.iterparse(source, ('start', 'end'), **kwargs))

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


##


@dc.dataclass(frozen=True)
class SimpleElement:
    tag: str
    attrs: ta.Mapping[str, str] | None = dc.xfield(default=None, repr_fn=dc.truthy_repr)
    body: ta.Sequence[ta.Union['SimpleElement', str]] | None = dc.xfield(default=None, repr_fn=dc.truthy_repr)

    #

    @cached.property
    def has_children(self) -> bool:
        return any(isinstance(c, SimpleElement) for c in self.body or ())

    @cached.property
    def children(self) -> ta.Sequence['SimpleElement']:
        return [c for c in self.body or () if isinstance(c, SimpleElement)]

    @cached.property
    def text(self) -> str:
        return ''.join(c for c in self.body or () if isinstance(c, str))

    #

    def se_dict(self) -> dict[str, ta.Any]:
        dct: dict[str, ta.Any] = {'tag': self.tag}
        if self.attrs:
            dct['attrs'] = self.attrs
        if self.body:
            dct['body'] = [
                c.se_dict() if isinstance(c, SimpleElement) else c
                for c in self.body
            ]
        return dct

    #

    def multidict(self) -> dict[str, list[ta.Any]]:
        dct: dict[str, list[ta.Any]] = {}

        for ce in self.children:
            try:
                cl = dct[ce.tag]
            except KeyError:
                dct[ce.tag] = cl = []

            if ce.has_children:
                cl.append(ce.multidict())
            elif ce.body:
                cl.append(ce.text)

        return dct


def build_simple_element(
        element: 'ET.Element',
        *,
        strip_tag_ns: bool = False,
) -> SimpleElement:
    def rec(cur: 'ET.Element') -> SimpleElement:
        atts = {}
        for name, value in cur.attrib.items():
            atts[name] = value  # noqa

        body: list[SimpleElement | str] = []

        if cur.text and (s := cur.text.strip()):
            body.append(s)

        for child in cur:
            body.append(rec(child))

            if child.tail and (s := child.tail.strip()):
                body.append(s)

        tag = cur.tag
        if strip_tag_ns:
            tag = strip_ns(tag)

        return SimpleElement(
            tag,
            atts,
            body,
        )

    return rec(element)


def parse_tree(s: str) -> 'ET.ElementTree':
    return ET.ElementTree(ET.fromstring(s.strip()))  # noqa
