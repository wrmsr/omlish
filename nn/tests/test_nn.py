import numpy as np

from ..dims import Shape
from ..dims import Stride
from ..dims import View
from ..lazy import LazyBuffer
from ..lazy import LazyOp
from ..ops import BinaryOp
from ..ops import LoadOp
from ..shapetracker import ShapeTracker


def test_nn():
    sh = Shape(1, 2, 3)
    st = Stride(3, 3, 3)
    v = View(sh, st)
    print(v)
    print(v.shape_strides)
    print(v.shape_strides)
    print(View.of_shape(sh))

    # t = Tensor()

    xa = np.asarray([1., 2.], dtype=np.float32)
    ya = np.asarray([3., 4.], dtype=np.float32)

    def make_load(a: np.ndarray) -> LazyBuffer:
        return LazyBuffer(
            ShapeTracker.of(Shape.of_np(a)),
            LazyOp(
                LoadOp.FROM_CPU,
                [],
                a,
            ),
        )

    xb = make_load(xa)
    yb = make_load(ya)

    zb = LazyBuffer(
        ShapeTracker.of(xb.shape),
        LazyOp(
            BinaryOp.MUL,
            [xb, yb],
        ),
    )

    za = zb.realize().realized().to_cpu()
    print(za)
