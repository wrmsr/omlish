import numpy as np

from ..dtypes import Float32
from ..devices import CpuDevice
from ..dims import Shape
from ..lazy import LazyBuffer
from ..lazy import LazyOp
from ..ops import BinaryOp
from ..ops import LoadOp
from ..shapetracker import ShapeTracker


def test_nn():
    # t = Tensor()

    xa = np.asarray([1., 2.], dtype=np.float32)
    ya = np.asarray([3., 4.], dtype=np.float32)

    def make_load(a: np.ndarray) -> LazyBuffer:
        return LazyBuffer(
            CpuDevice(),
            ShapeTracker.of(Shape.of_np(a)),
            LazyOp(
                LoadOp.FROM_CPU,
                [],
                a,
            ),
            Float32,
        )

    xb = make_load(xa)
    yb = make_load(ya)

    zb = LazyBuffer(
        CpuDevice(),
        ShapeTracker.of(xb.shape),
        LazyOp(
            BinaryOp.MUL,
            [xb, yb],
        ),
        Float32,
    )

    za = zb.realize().realized().to_cpu()
    print(za)
