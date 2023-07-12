import numpy as np

from .. import eval  # noqa
from ..arrays import get_aval
from ..arrays import raise_to_shaped
from ..batches import vmap
from ..jaxprs import make_jaxpr
from ..jaxprs import make_jaxpr_v1
from ..jaxprs import typecheck_jaxpr
from ..jvp import jvp
from ..jvp import jvp_v1
from ..prims import cos
from ..prims import mul
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


def test_jvp0():
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


def test_jvp1():
    def f(x):
        y = sin(x) * 2.
        z = - y + x
        return {'hi': z, 'there': [x, y]}

    x, xdot = 3., 1.
    y, ydot = jvp(f, (x,), (xdot,))
    print(y)
    print(ydot)

    print()


def test_batches0():
    def add_one_to_a_scalar(scalar):
        assert np.ndim(scalar) == 0
        return 1 + scalar

    vector_in = np.arange(3.)
    vector_out = vmap(add_one_to_a_scalar, (0,))(vector_in)

    print(vector_in)
    print(vector_out)

    print()


def test_batches1():
    def jacfwd(f, x):
        pushfwd = lambda v: jvp(f, (x,), (v,))[1]
        vecs_in = np.eye(np.size(x)).reshape(np.shape(x) * 2)
        return vmap(pushfwd, (0,))(vecs_in)

    def f(x):
        return sin(x)

    print(jacfwd(f, np.arange(3.)))

    print()


def test_jaxprs0():
    jaxpr, consts, _ = make_jaxpr_v1(lambda x: 2. * x, raise_to_shaped(get_aval(3.)))

    print(jaxpr)
    print(typecheck_jaxpr(jaxpr))

    print()


def test_jaxprs1():
    jaxpr, consts, _ = make_jaxpr(lambda: mul(2., 2.))
    print(jaxpr)
    print()
