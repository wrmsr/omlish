import ast
import textwrap

import astpretty

from ..expr import simple_interp_expr
from ..stmt import ReturnStmtResult
from ..stmt import simple_interp_stmt
from ..stmt import SimpleInterpStmtVisitor


def test_interp():
    astpretty.pprint(ast.parse(textwrap.dedent("""
    l[1,2,3:4,5:6]
    """), mode='exec'))

    astpretty.pprint(ast.parse(textwrap.dedent("""
    def f():
        x += 1
        nonlocal x
        return x
    # x = 0
    # assert f() == 2
    """), mode='exec'))

    assert simple_interp_expr('-1 + 2') == 1
    assert simple_interp_expr('1 < 2') is True
    assert simple_interp_expr('1 > 2') is False
    assert simple_interp_expr('[1, 2, 3]') == [1, 2, 3]
    assert simple_interp_expr('{1}') == {1}
    assert simple_interp_expr('{1: 2}') == {1: 2}
    assert simple_interp_expr('(1, 2)') == (1, 2)
    assert simple_interp_expr('set([1])') == {1}
    assert simple_interp_expr('"A".lower()') == 'a'
    assert simple_interp_expr('(lambda x: x + 1)(1)') == 2
    assert simple_interp_expr('1 if True else 0') == 1
    assert simple_interp_expr('[1, 2, 3][0]') == 1
    assert simple_interp_expr('[1, 2, 3][0:2]') == [1, 2]
    assert simple_interp_expr('[1, 2, 3][2:0:-1]') == [3, 2]
    assert simple_interp_expr('[1, 2, 3][-1]') == 3
    assert simple_interp_expr('[1, 2, 3][::-1]') == [3, 2, 1]
    assert simple_interp_expr('1 and 2') == 2
    assert simple_interp_expr('1 or 2') == 1
    assert simple_interp_expr('1 and []') == []
    assert simple_interp_expr('1 and [] and 3') == []
    assert simple_interp_expr('1 and [] or 3') == 3
    assert simple_interp_expr('...') is ...

    # assert simple_interp('[i * 2 for i in [1, 2]]') == [2, 4]

    interp = SimpleInterpStmtVisitor()
    simple_interp_stmt('def f(): return 1', interp=interp)
    assert interp.get_local('f')() == ReturnStmtResult(1)

    interp = SimpleInterpStmtVisitor()
    simple_interp_stmt(textwrap.dedent("""
    def f():
        x = 2
        return x
    """), interp=interp)
    assert interp.get_local('f')() == ReturnStmtResult(2)

    interp = SimpleInterpStmtVisitor()
    simple_interp_stmt(textwrap.dedent("""
    def f():
        x = 0
        for i in range(5):
            x = x + i
            x += 1
            if i >= 3:
                break
            1
        i = 0
        while i < 3:
            x *= 2
            i += 1
        return x
    """), interp=interp)
    assert interp.get_local('f')() == ReturnStmtResult(80)
