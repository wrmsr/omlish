from ... import check
from ..xml import build_simple_element
from ..xml import parse_tree


# https://www.w3schools.com/xml/xml_tree.asp
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


def test_simple_element() -> None:
    tree = parse_tree(DOC)

    el = build_simple_element(check.not_none(tree.getroot()))
    print(el)

    print(el.se_dict())
    print(el.multidict())
