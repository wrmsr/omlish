import os.path

import markdown_it as md

from ..incparse import IncrementalMarkdownParser


def test_incparse():
    with open(os.path.join(os.path.dirname(__file__), 'sample.md')) as f:
        src = f.read()

    parser = md.MarkdownIt().enable('table').enable('strikethrough')

    inc_parser = IncrementalMarkdownParser(parser=parser)

    inc_tokens: list = []
    for i in range(len(src)):
        inc_tokens = inc_parser.feed(src[i])
        assert inc_tokens

    assert inc_parser._num_stable_lines == 39  # noqa
    assert len(inc_parser._stable_tokens) == 113  # noqa

    real_tokens = parser.parse(src)

    assert inc_tokens == real_tokens
