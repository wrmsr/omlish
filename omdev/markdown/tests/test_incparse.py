import os.path

from markdown_it import MarkdownIt

from ..incparse import IncrementalMarkdownParser


def test_incparse():
    with open(os.path.join(os.path.dirname(__file__), 'sample.md')) as f:
        src = f.read()

    inc_parser = IncrementalMarkdownParser()

    inc_tokens: list = []
    for i in range(len(src)):
        inc_tokens = inc_parser.feed(src[i])
        assert inc_tokens

    assert inc_parser._num_stable_lines == 31  # noqa
    assert len(inc_parser._stable_tokens) == 66  # noqa

    real_tokens = MarkdownIt().parse(src)

    assert inc_tokens == real_tokens
