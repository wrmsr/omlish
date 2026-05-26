from .... import pdcmark as m
from ...blocks.machine import BlockMachine
from ...blocks.refdefs import parse_single_line_refdef
from ...options import COMMONMARK


def _feed(text):
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
    events.extend(bm.finish(offset))
    return events, bm.refdefs


# Scanner-level


def test_parse_basic():
    r = parse_single_line_refdef('[foo]: /url')
    assert r is not None
    label, ld = r
    assert label == 'foo' and ld.dest == '/url' and ld.title == ''


def test_parse_with_quoted_title():
    r = parse_single_line_refdef('[foo]: /url "the title"')
    assert r is not None
    label, ld = r
    assert ld.dest == '/url' and ld.title == 'the title'


def test_parse_with_paren_title():
    r = parse_single_line_refdef('[foo]: /url (the title)')
    assert r is not None and r[1].title == 'the title'


def test_parse_label_normalized():
    r = parse_single_line_refdef('[  FOO   bar  ]: /url')
    assert r is not None and r[0] == 'foo bar'


def test_parse_angle_dest():
    r = parse_single_line_refdef('[a]: <http://x.test>')
    assert r is not None and r[1].dest == 'http://x.test'


def test_parse_indent_up_to_3():
    r = parse_single_line_refdef('   [a]: /url')
    assert r is not None


def test_parse_indent_4_no():
    assert parse_single_line_refdef('    [a]: /url') is None


def test_parse_empty_label_no():
    assert parse_single_line_refdef('[]: /url') is None
    assert parse_single_line_refdef('[   ]: /url') is None


def test_parse_garbage_after_dest_no():
    assert parse_single_line_refdef('[a]: /url junk') is None


def test_parse_invalid_title_no():
    assert parse_single_line_refdef('[a]: /url "unterminated') is None


# BlockMachine integration


def test_refdef_consumed_no_paragraph_emitted():
    events, refdefs = _feed('[foo]: /url\n')
    # No events at all (refdef-only paragraph).
    assert events == []
    assert 'foo' in refdefs
    assert refdefs.get('foo').dest == '/url'


def test_refdef_followed_by_paragraph_in_same_block():
    events, refdefs = _feed('[foo]: /url\nactual text\n')
    # Refdef is consumed; remaining paragraph emits text.
    starts = [e for e in events if isinstance(e, m.Start)]
    assert len(starts) == 1 and isinstance(starts[0].tag, m.Paragraph)
    texts = [e.text for e in events if isinstance(e, m.Text)]
    assert texts == ['actual text']
    assert 'foo' in refdefs


def test_multiple_refdefs_stacked():
    events, refdefs = _feed('[a]: /a\n[b]: /b\n[c]: /c\n')
    assert events == []
    for k in ('a', 'b', 'c'):
        assert k in refdefs


def test_refdef_then_blank_then_use():
    events, refdefs = _feed('[foo]: /url\n\n[foo]\n')
    # Second paragraph is a shortcut link wrapping `foo` and resolving to the refdef.
    starts = [e for e in events if isinstance(e, m.Start)]
    tags = [type(s.tag).__name__ for s in starts]
    assert tags == ['Paragraph', 'Link']
    link_start = starts[1]
    assert link_start.tag.dest_url == '/url'  # type: ignore
    assert link_start.tag.link_type == m.LinkType.SHORTCUT  # type: ignore
    assert 'foo' in refdefs


def test_first_definition_wins():
    events, refdefs = _feed('[foo]: /first\n[foo]: /second\n')
    assert refdefs.get('foo').dest == '/first'


def test_setext_paragraph_is_not_refdef():
    # A paragraph that becomes a setext heading should NOT have refdefs peeled — `[foo]: /url\n===` is a level-1 heading
    # with content `[foo]: /url`.
    events, refdefs = _feed('[foo]: /url\n===\n')
    assert any(isinstance(e, m.Start) and isinstance(e.tag, m.Heading) for e in events)
    assert 'foo' not in refdefs


def test_non_refdef_first_line_stops_consumption():
    events, refdefs = _feed('not a refdef\n[foo]: /url\n')
    # The whole thing is ONE paragraph (the second line is paragraph continuation, not a fresh block). Refdef is NOT
    # peeled because it's mid-paragraph.
    paragraphs = [e for e in events if isinstance(e, m.Start) and isinstance(e.tag, m.Paragraph)]
    assert len(paragraphs) == 1
    assert 'foo' not in refdefs
