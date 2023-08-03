import textwrap

import pytest

from .. import items
from .. import rendering


@pytest.mark.skip()
def test_open_dot():
    src = textwrap.dedent("""
    digraph G {
        a;
        b;
        a -> b;
    }
    """)
    rendering.open_dot(src)


def test_dot():
    print(rendering.render(items.Value.of('hi')))
    print(rendering.render(items.Value.of([['a', 'b'], ['c', 'd']])))

    def print_and_open(no):
        print(no)
        gv = rendering.render(no)
        print(gv)
        # dot.open_dot(gv)

    print_and_open(items.Graph(
        [
            items.Node('a', {'shape': 'box'}),  # type: ignore
            items.Node('b', {'label': [['a', 'b'], ['c', 'd']]}),  # type: ignore
            items.Edge('a', 'b'),  # type: ignore
        ],
    ))
