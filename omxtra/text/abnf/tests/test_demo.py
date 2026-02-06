import os.path

import pytest

from omlish import check

from ..utils import fix_ws
from .demo import parse_demo_grammar


def test_demo_grammar():
    parse_demo_grammar()


@pytest.mark.parametrize('fn', [
    'demo.txt',
    'demo2.txt',
])
def test_demo(fn):
    gram = parse_demo_grammar()

    with open(os.path.join(os.path.dirname(__file__), fn)) as f:
        ast_src = f.read()

    ast_src = fix_ws(ast_src)

    print()
    m = check.not_none(gram.parse(
        ast_src,
        complete=True,
        # debug=True,
    ))
    print(m.render(indent=2))
