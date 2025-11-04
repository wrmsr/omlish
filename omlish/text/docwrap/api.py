import dataclasses as dc
import typing as ta

from ..textwrap import TextwrapOpts
from .groups import group_indents
from .lists import ListBuilder
from .parts import Part
from .parts import build_root
from .reflowing import TextwrapReflower
from .reflowing import reflow_block_text


##


DEFAULT_TAB_WIDTH: int = 4


def replace_tabs(s: str, tab_width: int | None = None) -> str:
    if tab_width is None:
        tab_width = DEFAULT_TAB_WIDTH
    return s.replace('\t', ' ' * tab_width)


##


def parse(
        s: str,
        *,
        tab_width: int | None = None,
        allow_improper_list_children: bool | ta.Literal['lists_only'] | None = None,
) -> Part:
    s = replace_tabs(
        s,
        tab_width=tab_width,
    )

    root = build_root(s)

    root = group_indents(root)

    root = ListBuilder(
        allow_improper_children=allow_improper_list_children,
    ).build_lists(root)

    return root


##


def docwrap(
        s: str,
        *,
        width: int | None = None,
        textwrap: TextwrapOpts | ta.Mapping[str, ta.Any] | None = None,
        allow_improper_list_children: bool | ta.Literal['lists_only'] = False,
) -> Part:
    if isinstance(textwrap, ta.Mapping):
        textwrap = TextwrapOpts(**textwrap)
    elif textwrap is None:
        textwrap = TextwrapOpts()
    if width is not None:
        textwrap = dc.replace(textwrap, width=width)

    root = parse(
        s,
        allow_improper_list_children=allow_improper_list_children,
    )

    root = reflow_block_text(
        root,
        TextwrapReflower(opts=textwrap),
    )

    return root
