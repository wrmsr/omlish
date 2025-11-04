"""
TODO:
 - a reflowing.TextReflower
 - import textwrap lol
 - obviously handle hyphens, underscores, etc
 - optionally preserve/normalize inter-sentence spaces - '.  ' vs '. '
 - detect if 'intentionally' smaller than current remaining line width, if so do not merge.
  - maybe if only ending with punctuation?
 - detect 'matched pairs' of 'quotes'? to preserve whitespace? `foo  bar` ...
  - how to escape it lol - if we see any \\` do we give up?
"""
import re
import typing as ta


SpanKind: ta.TypeAlias = ta.Literal[
    'word',
    'space',
    'symbol',
]


##


class Span(ta.NamedTuple):
    k: SpanKind
    s: str

    def __repr__(self) -> str:
        return f'{self.k}:{self.s!r}'


_SPAN_PAT = re.compile(r'(\w+)|(\s+)')


def split_line_spans(s: str) -> list[Span]:
    spans: list[Span] = []
    p = 0
    for m in _SPAN_PAT.finditer(s):
        l, r = m.span()
        if p < l:
            spans.append(Span('symbol', s[p:l]))
        if m.group(1):
            spans.append(Span('word', m.group(1)))
        else:
            spans.append(Span('space', m.group(2)))
        p = r
    if p < len(s):
        spans.append(Span('symbol', s[p:]))
    return spans


def _main() -> None:
    print(split_line_spans('hi i am a string! this has a hy-phen.'))


if __name__ == '__main__':
    _main()
