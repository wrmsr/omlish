import os.path

import pytest  # noqa

from omlish import check

from ..base import Grammar
from ..meta import parse_grammar
from ..utils import fix_ws


def parse_demo_grammar() -> Grammar:
    with open(os.path.join(os.path.dirname(__file__), 'demo.abnf')) as f:
        gram_src = f.read()

    return parse_grammar(
        gram_src,
        root='config',
        # debug=True,
    )


def test_demo_grammar():
    parse_demo_grammar()


# @pytest.mark.skip_unless_alone
def test_demo():
    gram = parse_demo_grammar()

    with open(os.path.join(os.path.dirname(__file__), 'demo.txt')) as f:
        ast_src = f.read()

    ast_src = fix_ws(ast_src)

    print()
    m = check.not_none(gram.parse(
        ast_src,
        complete=True,
        # debug=True,
    ))
    print(m.render(indent=2))
