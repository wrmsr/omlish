"""
https://www.w3schools.com/xml/xml_tree.asp

kinds:
 - element
 - attribute
 - text
"""
import xml.etree.ElementTree as ET


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


def _main() -> None:
    tree = ET.ElementTree(ET.fromstring(DOC.strip()))

    # def rec(node, pfx=''):
    #     print(f"{pfx}Element: {node.tag}")
    #     cpfx = pfx + '  '
    #     for name, value in node.attrib.items():
    #         print(f"{cpfx}  Attribute: {name} = {value}")
    #     for child in node:
    #         rec(child, cpfx)

    def recursive_process(element):
        lst = []
        for name, value in element.attrib.items():
            lst.append({'attribute': {name: value}})
        if element.text and element.text.strip():
            lst.append({'text': element.text.strip()})
        for child in element:
            child_lst = recursive_process(child)
            lst.append({'element': {child.tag: child_lst}})
            if child.tail and (tail_s := child.tail.strip()):
                lst.append({'text': tail_s})
        return lst

    print(recursive_process(tree.getroot()))

    # for elem in root.iter():
    #     print(f"Element: {elem.tag}")
    #     for name, value in elem.attrib.items():
    #         print(f"  Attribute: {name} = {value}")


if __name__ == '__main__':
    _main()
