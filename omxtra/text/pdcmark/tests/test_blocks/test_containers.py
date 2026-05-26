from .... import pdcmark as m
from ...blocks.machine import BlockMachine
from ...options import COMMONMARK
from ...options import GFM


def feed(text, *, options=COMMONMARK):
    bm = BlockMachine(options)
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
    events.extend(bm.finish(offset))
    return events


def kinds(events):
    return [
        (type(e).__name__, e.tag.__class__.__name__ if isinstance(e, (m.Start, m.End)) else None)
        for e in events
    ]


# Blockquotes


def test_simple_blockquote():
    out = feed('> foo\n')
    assert kinds(out) == [
        ('Start', 'BlockQuote'),
        ('Start', 'Paragraph'),
        ('Text', None),
        ('End', 'Paragraph'),
        ('End', 'BlockQuote'),
    ]


def test_blockquote_lazy_continuation():
    out = feed('> foo\nbar\n')
    starts = [e for e in out if isinstance(e, m.Start)]
    assert len(starts) == 2  # BlockQuote + Paragraph (no second paragraph)
    texts = [e.text for e in out if isinstance(e, m.Text)]
    assert texts == ['foo', 'bar']


def test_blockquote_explicit_continuation():
    out = feed('> foo\n> bar\n')
    starts = [e for e in out if isinstance(e, m.Start)]
    assert len(starts) == 2


def test_nested_blockquote():
    out = feed('> > nested\n')
    starts = [e for e in out if isinstance(e, m.Start)]
    assert [s.tag.__class__.__name__ for s in starts] == ['BlockQuote', 'BlockQuote', 'Paragraph']


def test_blockquote_closes_on_blank_then_paragraph():
    out = feed('> foo\n\nbar\n')
    starts = [e for e in out if isinstance(e, m.Start)]
    tags = [s.tag.__class__.__name__ for s in starts]
    assert tags == ['BlockQuote', 'Paragraph', 'Paragraph']


# Unordered lists


def test_simple_bullet_list():
    out = feed('- foo\n- bar\n')
    starts = [e for e in out if isinstance(e, m.Start)]
    tags = [s.tag.__class__.__name__ for s in starts]
    assert tags == ['List', 'Item', 'Paragraph', 'Item', 'Paragraph']
    list_start = next(e for e in out if isinstance(e, m.Start) and isinstance(e.tag, m.List))
    assert list_start.tag.start is None  # unordered


def test_ordered_list():
    out = feed('1. foo\n2. bar\n')
    list_start = next(e for e in out if isinstance(e, m.Start) and isinstance(e.tag, m.List))
    assert list_start.tag.start == 1


def test_ordered_list_arbitrary_start():
    out = feed('42. foo\n')
    list_start = next(e for e in out if isinstance(e, m.Start) and isinstance(e.tag, m.List))
    assert list_start.tag.start == 42


def test_different_marker_starts_new_list():
    out = feed('- foo\n+ bar\n')
    list_starts = [e for e in out if isinstance(e, m.Start) and isinstance(e.tag, m.List)]
    assert len(list_starts) == 2


def test_item_lazy_continuation():
    out = feed('- foo\nbar\n')
    paragraphs = [e for e in out if isinstance(e, m.Start) and isinstance(e.tag, m.Paragraph)]
    # Single paragraph carrying both lines.
    assert len(paragraphs) == 1
    texts = [e.text for e in out if isinstance(e, m.Text)]
    assert texts == ['foo', 'bar']


def test_item_indented_continuation():
    out = feed('- foo\n  bar\n')
    paragraphs = [e for e in out if isinstance(e, m.Start) and isinstance(e.tag, m.Paragraph)]
    assert len(paragraphs) == 1
    texts = [e.text for e in out if isinstance(e, m.Text)]
    assert texts == ['foo', 'bar']


def test_dedented_line_closes_list():
    out = feed('- foo\n\nbar\n')
    paragraphs = [e for e in out if isinstance(e, m.Start) and isinstance(e.tag, m.Paragraph)]
    # First paragraph in item, second outside.
    assert len(paragraphs) == 2


# Containers + leaves


def test_list_item_with_heading():
    out = feed('- # foo\n')
    tags = [s.tag.__class__.__name__ for s in out if isinstance(s, m.Start)]
    assert tags == ['List', 'Item', 'Heading']


def test_list_item_with_code_block_indent():
    out = feed('- foo\n\n      code\n')
    # The 6-space indent on "code" inside an item with content_indent=2 means 4 columns extra →
    # indented code block.
    tags = [s.tag.__class__.__name__ for s in out if isinstance(s, m.Start)]
    assert 'IndentedCodeBlock' in tags


def test_blockquote_containing_list():
    out = feed('> - foo\n')
    tags = [s.tag.__class__.__name__ for s in out if isinstance(s, m.Start)]
    assert tags == ['BlockQuote', 'List', 'Item', 'Paragraph']


def test_paragraph_then_list_interrupt():
    # Ordered list with start=1 may interrupt a paragraph.
    out = feed('para\n1. foo\n')
    starts = [s for s in out if isinstance(s, m.Start)]
    tags = [s.tag.__class__.__name__ for s in starts]
    assert tags == ['Paragraph', 'List', 'Item', 'Paragraph']


def test_paragraph_does_not_break_on_ordered_start_two():
    # Ordered start=2 does NOT interrupt a paragraph.
    out = feed('para\n2. foo\n')
    starts = [s for s in out if isinstance(s, m.Start)]
    tags = [s.tag.__class__.__name__ for s in starts]
    # Should be a single paragraph carrying both lines.
    assert tags == ['Paragraph']


# Task list (GFM)


def test_task_list_marker_off_by_default():
    out = feed('- [ ] task\n')
    assert not any(isinstance(e, m.TaskListMarker) for e in out)


def test_task_list_marker_with_gfm():
    out = feed('- [x] task\n', options=GFM)
    tlms = [e for e in out if isinstance(e, m.TaskListMarker)]
    assert len(tlms) == 1 and tlms[0].checked is True


def test_hrule_beats_bullet_list():
    out = feed('- - -\n')
    assert any(isinstance(e, m.Rule) for e in out)
    assert not any(isinstance(e, m.Start) and isinstance(e.tag, m.List) for e in out)


def test_deeply_nested_list_marker_starts_new_item():
    # Regression: a deeply-indented bullet marker must start a new item in the matching enclosing list, not be absorbed
    # by lazy continuation into the parent item's open paragraph. Before the fix, the lazy-continuation check evaluated
    # `_line_starts_new_block` against the RAW line (`      - C2`) — saw 6 leading spaces, treated as indented-code
    # territory, returned False, and lazy-extended the paragraph.
    src = '- A\n  - B\n    - C1\n    - C2\n    - C3\n'
    out = feed(src)
    list_starts = [e for e in out if isinstance(e, m.Start) and isinstance(e.tag, m.List)]
    item_starts = [e for e in out if isinstance(e, m.Start) and isinstance(e.tag, m.Item)]
    assert len(list_starts) == 3
    # outer A, middle B, inner C1/C2/C3 = 5 items total.
    assert len(item_starts) == 5
    texts = [e.text for e in out if isinstance(e, m.Text)]
    assert texts == ['A', 'B', 'C1', 'C2', 'C3']


# Finish


def test_finish_closes_open_containers():
    bm = BlockMachine(COMMONMARK)
    bm.feed_line('> - foo', 0, 8)
    out = bm.finish(8)
    # Expect End for Paragraph, Item, List, BlockQuote.
    ends = [e for e in out if isinstance(e, m.End)]
    assert [e.tag.__class__.__name__ for e in ends] == ['Paragraph', 'Item', 'List', 'BlockQuote']
