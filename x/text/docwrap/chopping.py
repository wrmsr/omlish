import typing as ta

from .groups import group_indents
from .joining import join_block_text
from .lists import ListBuilder
from .parts import Part
from .parts import build_root


##


DEFAULT_TAB_WIDTH: int = 4


def replace_tabs(s: str, tab_width: int = DEFAULT_TAB_WIDTH) -> str:
    return s.replace('\t', ' ' * tab_width)


#


def chop(
        s: str,
        *,
        allow_improper_list_children: bool | ta.Literal['lists_only'] = False,
) -> Part:
    s = replace_tabs(s)

    root = build_root(s)
    root = group_indents(root)
    root = ListBuilder(
        allow_improper_children=allow_improper_list_children,
    ).build_lists(root)
    root = join_block_text(root)

    return root
