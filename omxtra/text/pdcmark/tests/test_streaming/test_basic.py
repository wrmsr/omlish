"""Smoke tests for `StreamingParser` semantics."""
import pytest

from .... import pdcmark as m
from ...errors import ParserStateError
from ...streaming.parser import StreamingParser


def _all_committed(out_list):
    out = []
    for o in out_list:
        out.extend(o.committed)
    return out


def test_basic_oneshot_feed():
    sp = StreamingParser()
    fo1 = sp.feed('# Hi\n')
    fo2 = sp.finish()
    events = list(fo1.committed) + list(fo2.committed)
    assert events == m.parse('# Hi\n')


def test_empty_feed_is_noop():
    sp = StreamingParser()
    sp.feed('first ')
    prev_tentative = sp.feed('chunk\n').tentative
    out = sp.feed('')
    assert out.committed == ()
    assert out.tentative == prev_tentative


def test_finish_terminates():
    sp = StreamingParser()
    sp.finish()
    with pytest.raises(ParserStateError):
        sp.feed('x')


def test_finish_twice_is_idempotent():
    sp = StreamingParser()
    sp.finish()
    fo = sp.finish()
    assert fo.committed == ()
    assert fo.tentative == ()


def test_open_paragraph_appears_in_tentative():
    sp = StreamingParser()
    fo = sp.feed('hello ')
    # No newline → nothing committed, but tentative shows the paragraph that would close.
    assert fo.committed == ()
    text_events = [e for e in fo.tentative if isinstance(e, m.Text)]
    assert text_events and text_events[0].text == 'hello'


def test_tentative_updates_across_chunks():
    sp = StreamingParser()
    sp.feed('one ')
    fo = sp.feed('two ')
    texts = [e for e in fo.tentative if isinstance(e, m.Text)]
    assert texts and texts[0].text == 'one two'


def test_open_code_block_tentative():
    sp = StreamingParser()
    fo = sp.feed('```py\nx = 1\n')
    # The fence opened and one line of body went in. Tentative shows the open code block as if closed now.
    assert any(isinstance(e, m.Start) and isinstance(e.tag, m.FencedCodeBlock) for e in fo.tentative)
    texts = [e.text for e in fo.tentative if isinstance(e, m.Text)]
    assert texts == ['x = 1\n']


def test_committed_appended_only():
    """The same event should NOT appear in both committed and tentative across feeds."""

    sp = StreamingParser()
    all_committed: list = []
    chunks = ['# heading\n', 'paragraph ', 'more\n', '\n', 'second para\n']
    for chunk in chunks:
        fo = sp.feed(chunk)
        all_committed.extend(fo.committed)
    fo_end = sp.finish()
    all_committed.extend(fo_end.committed)
    # Compare with oneshot.
    expected = m.parse(''.join(chunks))
    assert all_committed == expected


def test_crlf_handling():
    src = '# title\r\nparagraph\r\n'
    sp = StreamingParser()
    fo = sp.feed(src)
    end = sp.finish()
    committed = list(fo.committed) + list(end.committed)
    assert committed == m.parse(src)


def test_cr_at_chunk_boundary():
    """CR ending one chunk + LF starting the next must form a single CRLF terminator, not two separate line breaks."""

    sp = StreamingParser()
    sp.feed('a\r')
    sp.feed('\nb\n')
    end = sp.finish()  # noqa
    committed = []  # noqa
    # Reconstruct from feeds. (We need to capture them all.)
    sp = StreamingParser()
    parts = ['a\r', '\nb\n']
    out: list = []
    for p in parts:
        out.extend(sp.feed(p).committed)
    out.extend(sp.finish().committed)
    expected = m.parse('a\r\nb\n')
    assert out == expected
