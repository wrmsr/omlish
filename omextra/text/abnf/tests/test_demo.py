import os.path

from omlish import check

from ..meta import parse_grammar
from ..utils import fix_ws


def test_demo():
    with open(os.path.join(os.path.dirname(__file__), 'demo.abnf')) as f:
        gram_src = f.read()

    gram = parse_grammar(
        gram_src,
        root='config',
        # debug=True,
    )

    with open(os.path.join(os.path.dirname(__file__), 'demo.txt')) as f:
        ast_src = f.read()

    ast_src = fix_ws(ast_src)

    m = check.not_none(gram.parse(ast_src))
    print(m.render(indent=2))
