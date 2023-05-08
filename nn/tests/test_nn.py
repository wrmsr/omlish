from ..dims import Shape
from ..dims import Stride
from ..dims import View


def test_nn():
    sh = Shape(1, 2, 3)
    st = Stride(3, 3, 3)
    v = View(sh, st)
    print(v)
    print(v.shape_strides)
    print(v.shape_strides)
    print(View.of_shape(sh))
