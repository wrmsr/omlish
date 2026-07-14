from omcore import marshal as msh

from ..rich import ui_text_to_rich_text
from ..text import DiffUiText
from ..text import UiText


def test_diff_ui_text():
    d = DiffUiText(
        old='a\nb\nc\n',
        new='a\nB\nc\n',
        path='f.py',
    )

    s = str(d)
    assert '--- f.py' in s
    assert '-b' in s
    assert '+B' in s

    rt = ui_text_to_rich_text(d)
    assert '+B' in rt.plain

    m = msh.marshal(d, UiText)
    d2 = msh.unmarshal(m, UiText)
    assert d2 == d
    assert msh.marshal(d2, UiText) == m


def test_diff_ui_text_composes():
    t = UiText.of([
        'changing f.py:\n',
        DiffUiText(old='x\n', new='y\n'),
    ])

    s = str(t)
    assert s.startswith('changing f.py:\n')
    assert '-x' in s
    assert '+y' in s
