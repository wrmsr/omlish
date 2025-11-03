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


_SPAN_PAT = re.compile(r'(\w)|(\s+)')


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
    print(split_line_spans('hi i am a string!'))


if __name__ == '__main__':
    _main()
