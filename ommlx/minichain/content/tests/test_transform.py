from ..placeholders import Env
from ..placeholders import EnvKey
from ..placeholders import Placeholder
from ..transform import PlaceholderFiller
from ..transform import StringRenderer


def test_transform():
    c = [
        'foo ',
        [
            'bar ',
            Placeholder(EnvKey('huh')),
            ' baz',
        ],
        ' fff',
    ]

    c2 = PlaceholderFiller(Env({'huh': 'what', 'no': 'yes'})).apply(c)
    s = StringRenderer.render_to_str(c2)
    assert s == 'foo bar what baz fff'
