import os.path

from ..meta import parse_grammar


def test_demo():
    with open(os.path.join(os.path.dirname(__file__), 'demo.abnf')) as f:
        gram_src = f.read()

    gram = parse_grammar(gram_src, root='config')

    with open(os.path.join(os.path.dirname(__file__), 'demo.txt')) as f:
        ast_src = f.read()

    m = gram.parse(ast_src)
    assert m is not None
