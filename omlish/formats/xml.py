"""
TODO:
 - lxml abstraction
 - stuff from ommlx/wiki
"""
import typing as ta

from .. import dataclasses as dc
from .. import lang


if ta.TYPE_CHECKING:
    import xml.etree.ElementTree as ET
else:
    ET = lang.proxy_import('xml.etree.ElementTree')


##


@dc.dataclass(frozen=True)
class SimpleElement:
    tag: str
    attributes: ta.Mapping[str, str] | None = dc.xfield(default=None, repr_fn=dc.truthy_repr)
    body: ta.Sequence[ta.Union['SimpleElement', str]] | None = dc.xfield(default=None, repr_fn=dc.truthy_repr)

    def as_dict(self) -> dict[str, ta.Any]:
        dct: dict[str, ta.Any] = {'tag': self.tag}
        if self.attributes:
            dct['attributes'] = self.attributes
        if self.body:
            dct['body'] = [
                c.as_dict() if isinstance(c, SimpleElement) else c
                for c in self.body
            ]
        return dct


def build_simple_element(element: 'ET.Element') -> SimpleElement:
    atts = {}
    for name, value in element.attrib.items():
        atts[name] = value  # noqa

    body: list[SimpleElement | str] = []

    if element.text and (s := element.text.strip()):
        body.append(s)

    for child in element:
        body.append(build_simple_element(child))

        if child.tail and (s := child.tail.strip()):
            body.append(s)

    return SimpleElement(
        element.tag,
        atts,
        body,
    )


def parse_tree(s: str) -> 'ET.ElementTree':
    return ET.ElementTree(ET.fromstring(s.strip()))  # noqa
