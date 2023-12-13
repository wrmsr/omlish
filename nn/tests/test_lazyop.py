import time
import unittest

import numpy as np

from ..lazy import LazyBuffer
# stuff needed to unpack a kernel
# ruff: noqa: F401
from ..ops import (
    BinaryOps,
)
from ..tensor import Tensor

inf, nan = float("inf"), float("nan")


class TestLazyOp(unittest.TestCase):
    def test_lazyop_str(self):
        t = Tensor.rand(10) + Tensor.rand(10)
        s = t.lazydata.schedule()
        ast = s[-1].ast
        ast_remade = eval(str(ast))
        self.assertEqual(ast, ast_remade)

    def test_selfreferential_speed(self):
        st = time.monotonic()
        for i in range(25):
            p = LazyBuffer.fromCPU(np.array([1]))
            for _ in range(i):
                p = p.e(BinaryOps.ADD, p)
            # sanity check if caching works this should be way faster
            assert time.monotonic() - st < 0.5, f"{i}"


if __name__ == "__main__":
    unittest.main()
