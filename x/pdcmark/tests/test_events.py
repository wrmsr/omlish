import dataclasses as dc

import pytest

from ... import pdcmark as m


def test_tag_is_abstract():
    with pytest.raises(TypeError):
        m.Tag()


def test_event_is_abstract():
    with pytest.raises(TypeError):
        m.Event()


def test_concrete_tags_construct():
    m.Paragraph()
    m.Heading(level=1)
    m.BlockQuote()
    m.BlockQuote(kind=m.BlockQuoteKind.NOTE)
    m.FencedCodeBlock(info='')
    m.FencedCodeBlock(info='python')
    m.IndentedCodeBlock()
    m.HtmlBlock()
    m.List()
    m.List(start=1)
    m.List(start=1, tight=False)
    m.Item()
    m.Table(alignments=[m.Alignment.LEFT, m.Alignment.NONE])
    m.TableHead()
    m.TableRow()
    m.TableCell()
    m.Emphasis()
    m.Strong()
    m.Strikethrough()
    m.Link(link_type=m.LinkType.INLINE, dest_url='http://x', title='', id='')
    m.Image(link_type=m.LinkType.INLINE, dest_url='http://x', title='', id='')


def test_concrete_events_construct():
    p = m.Paragraph()
    m.Start(offset=(0, 5), tag=p)
    m.End(offset=(0, 5), tag=p)
    m.Text(offset=(0, 5), text='hello')
    m.Code(offset=(0, 5), text='x')
    m.Html(offset=(0, 5), text='<p>')
    m.InlineHtml(offset=(0, 5), text='<br/>')
    m.SoftBreak(offset=(5, 6))
    m.HardBreak(offset=(5, 6))
    m.Rule(offset=(0, 3))
    m.TaskListMarker(offset=(0, 3), checked=True)


def test_events_are_frozen():
    t = m.Text(offset=(0, 5), text='hi')
    with pytest.raises(dc.FrozenInstanceError):
        t.text = 'no'  # type: ignore[misc]


def test_tags_are_frozen():
    h = m.Heading(level=2)
    with pytest.raises(dc.FrozenInstanceError):
        h.level = 1  # type: ignore[misc]


def test_isinstance_discriminants():
    assert isinstance(m.Paragraph(), m.Tag)
    assert isinstance(m.Heading(level=1), m.Tag)
    assert isinstance(m.Link(link_type=m.LinkType.INLINE, dest_url='', title='', id=''), m.Tag)
    p = m.Paragraph()
    assert isinstance(m.Start(offset=(0, 1), tag=p), m.Event)
    assert isinstance(m.Text(offset=(0, 1), text=''), m.Event)


def test_list_tight_default_none():
    assert m.List().tight is None
    assert m.List(start=1).tight is None
    assert m.List(tight=False).tight is False
    assert m.List(tight=True).tight is True
