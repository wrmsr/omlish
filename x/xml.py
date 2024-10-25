"""
https://www.w3schools.com/xml/xml_tree.asp

kinds:
 - element
 - attribute
 - text
"""
import typing as ta

from omlish import dataclasses as dc
from omlish import lang


if ta.TYPE_CHECKING:
    import xml.etree.ElementTree as ET
else:
    ET = lang.proxy_import('xml.etree.ElementTree')


##


DOC = """
<?xml version="1.0" encoding="UTF-8"?>
<bookstore>
  <book category="cooking">
    <title lang="en">Everyday Italian</title>
    <author>Giada De Laurentiis</author>
    foo
    <year>2005</year>
    <price>30.00</price>
  </book>
  <book category="children">
    <title lang="en">Harry Potter</title>
    <author>J K. Rowling</author>
    <year>2005</year>
    <price>29.99</price>
  </book>
  <book category="web">
    <title lang="en">Learning XML</title>
    <author>Erik T. Ray</author>
    <year>2003</year>
    <price>39.95</price>
  </book>
</bookstore>
"""


@dc.dataclass(frozen=True)
class SimpleElement:
    tag: str
    attributes: ta.Mapping[str, str] | None = dc.xfield(default=None, repr_fn=dc.truthy_repr)
    body: ta.Sequence[ta.Union['SimpleElement', str]] | None = dc.xfield(default=None, repr_fn=dc.truthy_repr)


def build_simple_element(element: 'ET.Element') -> SimpleElement:
    atts = {}
    for name, value in element.attrib.items():
        atts[name] = value

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


def _main() -> None:
    tree = ET.ElementTree(ET.fromstring(DOC.strip()))

    print(build_simple_element(tree.getroot()))

    # for elem in root.iter():
    #     print(f"Element: {elem.tag}")
    #     for name, value in elem.attrib.items():
    #         print(f"  Attribute: {name} = {value}")


if __name__ == '__main__':
    _main()
