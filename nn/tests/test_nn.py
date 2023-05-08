import numpy as np

from ..dims import Shape
from ..dims import Stride
from ..dims import View
from ..lazy import LazyBuffer
from ..lazy import LazyOp
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

    x = np.asarray([1, 2])
    y = np.asarray([3, 4])

    xb = LazyBuffer(
        ShapeTracker.of(Shape.of_np(x)),
        LazyOp(
            LoadOp.FROM_CPU,
            [],
            x,
        ),
    )

    """
    func MakeLoadBuffer(data *Buffer) *LazyBuffer {
        return NewLazyBuffer(
            NewShapeTracker(data.Shape()),
            LoadOpType,
            &LazyOp{
                op:   FromCpuOp,
                srcs: nil,
                arg:  data,
            },
        )
    }
    """
