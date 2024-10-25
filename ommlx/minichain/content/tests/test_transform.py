from ..placeholders import Env
from ..placeholders import EnvKey
from ..placeholders import Placeholder
from ..transform import PlaceholderTransform


def test_transform():
    c = [
        'foo',
        [
            'bar',
            Placeholder(EnvKey('huh')),
            'baz',
        ],
        'fff,'
    ]

    print(PlaceholderTransform(Env({'huh': 'what', 'no': 'yes'})).apply(c))
