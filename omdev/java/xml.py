"""
TODO:
 -> omlish.formats.xml
"""
import typing as ta
import xml.etree.ElementTree as ET
import xml.sax.saxutils


##


def append_xml_tail(el: ET.Element, tail: str, *, delim: str = '') -> ET.Element:
    el.tail = ((el.tail + delim) if el.tail else '') + tail
    return el


def scalar_to_xml_text(obj: ta.Any) -> str:
    if isinstance(obj, bool):
        return 'true' if obj else 'false'

    elif isinstance(obj, (int, float, str)):
        return str(obj)

    else:
        raise TypeError(obj)


def val_to_xml(tag: str, obj: ta.Any, *, tail: str | None = None) -> ET.Element:
    el = ET.Element(tag)

    if isinstance(obj, dict):
        for k, v in obj.items():
            el.append(val_to_xml(k, v))

    elif isinstance(obj, list):
        for item in obj:
            el.append(val_to_xml(tag, item))

    else:
        el.text = scalar_to_xml_text(obj)

    if tail is not None:
        el.tail = tail

    return el


def append_xml_val(parent: ET.Element, tag: str, val: ta.Any, *, tail: str | None = None) -> ET.Element:
    el = val_to_xml(tag, val, tail=tail)
    parent.append(el)
    return el


def indent_xml(
        root: ET.Element,
        space: str = '  ',
        level: int = 0,
        *,
        keep_space_tails: bool = False,
) -> None:
    """
    Indent an XML document by inserting newlines and indentation space after elements.

    *root* is the ElementTree or Element to modify.  The (root) element itself will not be changed, but the tail text of
    all elements in its subtree will be adapted.

    *space* is the whitespace to insert for each indentation level, two space characters by default.

    *level* is the initial indentation level. Setting this to a higher value than 0 can be used for indenting subtrees
    that are more deeply nested inside of a document.
    """

    if isinstance(root, ET.ElementTree):
        root = root.getroot()
    if level < 0:
        raise ValueError(f'Initial indentation level must be >= 0, got {level}')
    if not len(root):
        return

    # Reduce the memory consumption by reusing indentation strings.
    indentations = ['\n' + level * space]

    def rec(el: ET.Element, level: int) -> None:
        # Start a new indentation level for the first child.
        child_level = level + 1
        try:
            child_indentation = indentations[child_level]
        except IndexError:
            child_indentation = indentations[level] + space
            indentations.append(child_indentation)

        if not el.text or not el.text.strip():
            el.text = child_indentation

        for child in el:
            if len(child):
                rec(child, child_level)
            if keep_space_tails and child.tail and not child.tail.strip():
                child.tail += child_indentation
            elif not child.tail or not child.tail.strip():
                child.tail = child_indentation

        # Dedent after the last child by overwriting the previous indentation.
        if not child.tail.strip():  # type: ignore[union-attr]
            child.tail = indentations[level]

    rec(root, 0)


def render_xml_node_head(tag: str, atts: ta.Mapping[str, str], *, indent: str = '  ') -> str:
    if not atts:
        return f'<{tag}>'

    return '\n'.join([
        f'<{tag}',
        *[f'{indent}{k}={xml.sax.saxutils.quoteattr(v)}' for k, v in atts.items()],
        '>',
    ])
