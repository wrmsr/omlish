from .. import tokenize as tok_


def test_brace_indent():
    l = 'if x: { x += 1 }; print(x)'
    r = tok_.brace_indent(l)
    e = 'if x :\n    x += 1 \n\nprint ( x )   \n'
    assert r == e

    l = 'if x: { x += 1; y += 2 }; print(x)'
    r = tok_.brace_indent(l)
    e = 'if x :\n    x += 1 \n    y += 2 \n\nprint ( x )   \n'
    assert r == e
