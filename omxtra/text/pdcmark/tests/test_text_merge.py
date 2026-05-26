from ... import pdcmark as m


def test_merges_consecutive_text():
    out = list(m.merge_text([
        m.Text(offset=(0, 3), text='abc'),
        m.Text(offset=(3, 6), text='def'),
        m.Text(offset=(6, 9), text='ghi'),
    ]))
    assert out == [m.Text(offset=(0, 9), text='abcdefghi')]


def test_preserves_interleaved_non_text():
    out = list(m.merge_text([
        m.Text(offset=(0, 3), text='abc'),
        m.Text(offset=(3, 6), text='def'),
        m.Rule(offset=(6, 9)),
        m.Text(offset=(9, 12), text='xyz'),
    ]))
    assert out == [
        m.Text(offset=(0, 6), text='abcdef'),
        m.Rule(offset=(6, 9)),
        m.Text(offset=(9, 12), text='xyz'),
    ]


def test_drops_empty_text():
    out = list(m.merge_text([
        m.Rule(offset=(0, 1)),
        m.Text(offset=(1, 1), text=''),
        m.Text(offset=(1, 1), text=''),
        m.Rule(offset=(1, 2)),
    ]))
    assert out == [m.Rule(offset=(0, 1)), m.Rule(offset=(1, 2))]


def test_pass_through_when_no_text():
    p = m.Paragraph()
    evs = [m.Start(offset=(0, 5), tag=p), m.End(offset=(0, 5), tag=p)]
    assert list(m.merge_text(evs)) == evs


def test_empty_input():
    assert list(m.merge_text([])) == []


def test_single_text():
    out = list(m.merge_text([m.Text(offset=(0, 3), text='abc')]))
    assert out == [m.Text(offset=(0, 3), text='abc')]


def test_trailing_text_flushed():
    out = list(m.merge_text([
        m.Rule(offset=(0, 3)),
        m.Text(offset=(3, 4), text='a'),
        m.Text(offset=(4, 5), text='b'),
    ]))
    assert out == [m.Rule(offset=(0, 3)), m.Text(offset=(3, 5), text='ab')]
