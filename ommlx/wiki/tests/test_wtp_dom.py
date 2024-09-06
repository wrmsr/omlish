"""
https://en.wikipedia.org/wiki/Help:Wikitext
https://www.mediawiki.org/wiki/Alternative_parsers

wtp:
https://github.com/5j9/wikitextparser ??
https://github.com/TrueBrain/TrueWiki
https://github.com/TrueBrain/wikitexthtml
  Argument
  Bold
  Comment
  ExternalLink
  Italic
  Parameter
  ParserFunction
  Section
  Table
  Tag
  Template
  WikiLink
  WikiList
  WikiText


"""
import dataclasses as dc
import heapq
import importlib.resources
import itertools
import typing as ta  # noqa

import wikitextparser as wtp

from omlish import cached


##


@dc.dataclass(frozen=True)
class WtpNode:
    wiki: wtp.WikiText
    children: list[ta.Union['WtpNode', str]] = dc.field(default_factory=list)

    @cached.property
    def span(self) -> tuple[int, int]:
        return self.wiki.span  # noqa


def build_wtp_tree(src: str) -> WtpNode:
    wiki = wtp.parse(src)

    part_its = [
        wiki.parameters,
        wiki.parser_functions,
        wiki.templates,
        wiki.wikilinks,
        wiki.comments,
        wiki.get_bolds_and_italics(),
        wiki.external_links,
        wiki.sections,
        wiki.get_tables(recursive=True),
        wiki.get_lists(),
        wiki.get_tags(),
    ]

    #

    flat_it = itertools.chain.from_iterable(
        sorted(
            [o for _, o in g],
            key=lambda o: -o.span[1],
        )
        for _, g in itertools.groupby(
            heapq.merge(*[
                ((o.span, o) for o in it)
                for it in part_its
            ]),
            key=lambda t: t[0][0],
        )
    )

    #

    root = WtpNode(wiki)
    stk: list[WtpNode] = [root]

    o: wtp.WikiText
    for o in flat_it:
        p = None
        while o.span[0] >= stk[-1].wiki.span[1]:
            p = stk.pop()
            stk[-1].children.append(p)

        if p is not None:
            l, r = p.wiki.span[1], o.span[0]
            if l > r:
                raise Exception(f'{p.wiki.span=} {o.span=}')
            if (r - l) > 1:
                stk[-1].children.append(src[l:r])

        stk.append(WtpNode(o))

    while len(stk) > 1:
        p = stk.pop()
        stk[-1].children.append(p)

    if stk.pop() is not root:
        raise RuntimeError

    return root


##


def test_dom():
    src = importlib.resources.files(__package__).joinpath('test.wiki').read_text()

    root = build_wtp_tree(src)  # noqa

    print('!! DONE')