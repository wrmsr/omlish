"""
TODO:

 ['def' {'foo': int}, ['a', ['b', 1], {'c': int}. [{'d': int}, 2]],
  ['return', ['+', ['+', ['+', 'a', 'b'], 'c'], 'd']]]

 ['def', 'foo', ['*args', '**kwargs'],
  ['return', True]]
"""
import ast

from .. import nodes as no  # noqa
from .. import rendering as ren
from .. import sexprs


def test_sexprs():
    print()

    for s in [

        # (def add2 (x y)
        #  (return (+ x 2)))
        ['def', 'add2', ['x', 'y'],
         ['return', ['+', 'x', 2]]],

        # (def say_hi ()
        #  (print 'hi'))
        ['def', 'say_hi', [],
         ['print', '~hi']],

        # (def barf (x)
        #  (y= (+ x 2))
        #  (return y))
        ['def', 'barf', ['x'],
         ['y=', ['+', 'x', 2]],
         ['return', 'y']],

        # (def pt_thing (pt)
        #  (.x= pt (+ (.x pt) (.y pt)))
        #  (return pt))
        ['def', 'pt_thing', ['pt'],
         ['.x=', 'pt', ['+', ['.x', 'pt'], ['.y', 'pt']]],
         ['return', 'pt']],

        # (def ls (l0 l1)
        #  (:[= l0 0 (:[ l1 1)))
        ['def', 'ls', ['l0', 'l1'],
         ['[=', 'l0', 0, ['[', 'l1', 1]]],

    ]:
        print(s)

        t = sexprs.xlat(s)
        print(t)

        rd = ren.render(t)
        print(rd.strip())

        ar2 = ast.parse(rd, 'exec')
        print(ar2)

        print()
