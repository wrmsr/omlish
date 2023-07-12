from .. import eval  # noqa
from ..jvp import jvp_v1
from ..prims import cos
from ..prims import sin


def test_jax0():
    def foo():
        def f(x):
            y = sin(x) * 2.
            z = - y + x
            return z

        print(f(3.0))

        print()

    foo()


def test_jvp():
    x = 3.0
    y, sin_deriv_at_3 = jvp_v1(sin, (x,), (1.0,))
    print(sin_deriv_at_3)
    print(cos(3.0))

    print()

    def f(x):
        y = sin(x) * 2.
        z = - y + x
        return z

    x, xdot = 3., 1.
    y, ydot = jvp_v1(f, (x,), (xdot,))
    print(y)
    print(ydot)

    print()

    def deriv(f):
        return lambda x: jvp_v1(f, (x,), (1.,))[1]

    print(deriv(sin)(3.))
    print(deriv(deriv(sin))(3.))
    print(deriv(deriv(deriv(sin)))(3.))
    print(deriv(deriv(deriv(deriv(sin))))(3.))

    print()
