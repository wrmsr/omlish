import inspect

import pytest

from .. import argspecs as argspecs_
from .. import gen as gen_
from .. import names as names_


def test_codegen():
    def run(fn):
        nsb = names_.NamespaceBuilder()
        argspecs_.render_arg_spec_def(argspecs_.ArgSpec.from_inspect(inspect.getfullargspec(fn)), nsb)

    run(lambda: None)
    run(lambda a: None)
    run(lambda a=0: None)
    run(lambda a, b: None)
    run(lambda a, b=0: None)
    run(lambda a=0, b=0: None)
    run(lambda a, b, *c: None)
    run(lambda a, b, *, c: None)
    run(lambda a, b, *, c=0: None)
    run(lambda a, b, *, c=0, **k: None)


def test_indent():
    g = gen_.IndentWriter()
    g.write('hi\n')
    with g.indent():
        g.write('a ')
        g.write('there\n')
    g.write('barf')

    print()
    print(g.getvalue())


def test_createfn():
    fn = gen_.create_function('fn', gen_.ArgSpec(['x', 'y']), 'return x + y')
    assert fn(1, 2) == 3

    fn = gen_.create_function('fn', gen_.ArgSpec(['x', 'y']), 'raise ValueError')
    with pytest.raises(ValueError):
        assert fn(1, 2) == 3
