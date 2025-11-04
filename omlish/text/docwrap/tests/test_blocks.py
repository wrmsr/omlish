from ..parts import Block
from ..parts import Indent
from ..parts import Text
from ..parts import blockify


def test_blockify():
    assert blockify(
        Text('hi'),
        Block([Text('foo'), Text('foo2')]),
        Block([Text('bar'), Text('bar2')]),
    ) == Block([
        Text('hi'),
        Text('foo'),
        Text('foo2'),
        Text('bar'),
        Text('bar2'),
    ])

    assert blockify(
        Text('hi'),
        Indent(2, Text('a')),
        Indent(2, Text('b')),
    ) == Block([
        Text('hi'),
        Indent(2, Block((
            Text('a'),
            Text('b'),
        ))),
    ])
