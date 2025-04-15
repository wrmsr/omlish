from ..bracepy import translate_brace_python


def test_bracepy():
    ns: dict = {}
    exec(translate_brace_python('def f(x): { x += 2; return x }'), ns)
    assert ns['f'](3) == 5

    ns = {}
    exec(translate_brace_python('class Foo: { def __init__(self, x): { self._x = x } def f(self, x): { return self._x + x } }'), ns)  # noqa
    assert ns['Foo'](3).f(4) == 7
