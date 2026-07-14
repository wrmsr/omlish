"""
TODO:
 - Lists?
 - Tags
"""
from omlish.text import docwrap as dw

from ..content import Content


##


def parse_simple_content(s: str) -> Content:
    s = s.lstrip('\n').rstrip()

    root = dw.parse(s, ignore_lists=True)
    root = dw.reflow_block_text(root)

    if isinstance(root, dw.Indent):
        root = root.p

    xs = dw.render(root)

    return xs
