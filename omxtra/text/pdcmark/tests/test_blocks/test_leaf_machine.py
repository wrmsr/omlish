import pytest

from .... import pdcmark as m
from ...blocks.machine import BlockMachine
from ...options import COMMONMARK


def feed(text, *, do_finish=True):
    bm = BlockMachine(COMMONMARK)
    events = []
    offset = 0
    for line in text.splitlines(keepends=True):
        if line.endswith('\r\n'):
            nl = 2
            body = line[:-2]
        elif line.endswith(('\n', '\r')):
            nl = 1
            body = line[:-1]
        else:
            nl = 0
            body = line
        next_off = offset + len(body) + nl
        events.extend(bm.feed_line(body, offset, next_off))
        offset = next_off
    if do_finish:
        events.extend(bm.finish(offset))
    return events


def tags(events):
    return [
        (type(e).__name__, getattr(e, 'tag', None).__class__.__name__ if isinstance(e, (m.Start, m.End)) else None)
        for e in events
    ]


def test_atx_emits_heading():
    out = feed('# Title\n')
    assert tags(out) == [('Start', 'Heading'), ('Text', None), ('End', 'Heading')]
    assert out[0].tag.level == 1
    assert out[1].text == 'Title'


def test_atx_levels():
    for level in range(1, 7):
        out = feed('#' * level + ' h\n')
        assert isinstance(out[0], m.Start) and out[0].tag.level == level  # type: ignore


def test_paragraph_emits_paragraph():
    out = feed('hello\n')
    assert tags(out) == [('Start', 'Paragraph'), ('Text', None), ('End', 'Paragraph')]


def test_paragraph_multiline_with_softbreaks():
    out = feed('a\nb\nc\n')
    kinds = [type(e).__name__ for e in out]
    assert kinds == ['Start', 'Text', 'SoftBreak', 'Text', 'SoftBreak', 'Text', 'End']


def test_blank_separates_paragraphs():
    out = feed('a\n\nb\n')
    starts = [e for e in out if isinstance(e, m.Start)]
    assert len(starts) == 2
    assert all(isinstance(s.tag, m.Paragraph) for s in starts)


def test_hrule():
    out = feed('---\n')
    assert len(out) == 1 and isinstance(out[0], m.Rule)


def test_hrule_alternatives():
    for s in ['***\n', '___\n', '- - -\n', '   ***\n']:
        out = feed(s)
        assert len(out) == 1 and isinstance(out[0], m.Rule), s


def test_setext_h1_and_h2():
    out = feed('Title\n===\n')
    assert isinstance(out[0], m.Start) and out[0].tag.level == 1  # type: ignore
    out = feed('Title\n---\n')
    assert isinstance(out[0], m.Start) and out[0].tag.level == 2  # type: ignore


def test_setext_only_applies_to_open_paragraph():
    # `===` on its own at the start of input is not a setext (no prior paragraph).
    out = feed('===\n')
    # It should be interpreted as a paragraph containing `===`.
    assert isinstance(out[0], m.Start) and isinstance(out[0].tag, m.Paragraph)


def test_fenced_code_block():
    out = feed('```py\nfoo\nbar\n```\n')
    assert isinstance(out[0], m.Start) and isinstance(out[0].tag, m.FencedCodeBlock)
    assert out[0].tag.info == 'py'
    texts = [e.text for e in out if isinstance(e, m.Text)]
    assert texts == ['foo\n', 'bar\n']
    assert isinstance(out[-1], m.End)


def test_fenced_code_closes_at_eof():
    # No close fence - should still emit a valid code block at finish.
    out = feed('```\nfoo\n')
    assert isinstance(out[0], m.Start) and isinstance(out[0].tag, m.FencedCodeBlock)
    assert isinstance(out[-1], m.End)


def test_indented_code():
    out = feed('    code\n    more\n')
    assert isinstance(out[0].tag, m.IndentedCodeBlock)
    texts = [e.text for e in out if isinstance(e, m.Text)]
    assert texts == ['code\n', 'more\n']


def test_indented_code_strips_trailing_blanks():
    out = feed('    code\n\n')
    texts = [e.text for e in out if isinstance(e, m.Text)]
    assert texts == ['code\n']


def test_indented_after_paragraph_is_lazy_continuation():
    # Indentation does NOT start a code block when a paragraph is open; it's lazy continuation.
    out = feed('para\n    still para\n')
    # One paragraph, two text lines + a softbreak.
    starts = [e for e in out if isinstance(e, m.Start)]
    assert len(starts) == 1 and isinstance(starts[0].tag, m.Paragraph)


def test_html_block_type_6():
    out = feed('<div>\nhello\n</div>\n')
    assert isinstance(out[0].tag, m.HtmlBlock)
    htmls = [e for e in out if isinstance(e, m.Html)]
    assert [h.text for h in htmls] == ['<div>\n', 'hello\n', '</div>\n']


def test_html_block_type_2_comment():
    out = feed('<!-- comment -->\n')
    assert isinstance(out[0].tag, m.HtmlBlock)


def test_html_block_type_1_closes_on_marker_line():
    out = feed('<script>\nfoo\n</script>\nafter\n')
    # After </script> we should close the html block; "after" is its own paragraph.
    html_end_ix = next(i for i, e in enumerate(out) if isinstance(e, m.End) and isinstance(e.tag, m.HtmlBlock))
    later_starts = [e for e in out[html_end_ix + 1:] if isinstance(e, m.Start)]
    assert later_starts and isinstance(later_starts[0].tag, m.Paragraph)


def test_atx_interrupts_paragraph():
    out = feed('para\n# heading\n')
    starts = [e for e in out if isinstance(e, m.Start)]
    assert isinstance(starts[0].tag, m.Paragraph)
    assert isinstance(starts[1].tag, m.Heading)


def test_hrule_interrupts_paragraph():
    out = feed('para\n---\n')
    # Tricky case: `para\n---\n` is actually a setext-H2, NOT paragraph + hrule, per CM spec. Setext promotion wins
    # because the underline is checked before paragraph-interrupters.
    assert isinstance(out[0].tag, m.Heading) and out[0].tag.level == 2


def test_fence_interrupts_paragraph():
    out = feed('para\n```\ncode\n```\n')
    starts = [e for e in out if isinstance(e, m.Start)]
    assert isinstance(starts[0].tag, m.Paragraph)
    assert isinstance(starts[1].tag, m.FencedCodeBlock)


def test_finish_closes_open_paragraph():
    bm = BlockMachine(COMMONMARK)
    bm.feed_line('a', 0, 2)
    out = bm.finish(2)
    assert isinstance(out[0], m.Start) and isinstance(out[0].tag, m.Paragraph)
    assert isinstance(out[-1], m.End)


def test_finish_terminates_machine():
    bm = BlockMachine(COMMONMARK)
    bm.finish(0)
    with pytest.raises(RuntimeError):
        bm.feed_line('x', 0, 2)
