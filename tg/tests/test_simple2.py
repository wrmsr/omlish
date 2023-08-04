import unittest

import numpy as np
import torch

from tinygrad.tensor import Tensor


class TestSimple(unittest.TestCase):
    def test_simple_bin2red(self):
        a = 0.
        b = 1.
        x, y, z = [Tensor(np.random.random(size=(16, 16)).astype(np.float32) + a) * b for _ in range(3)]
        i = ((x * 0.420) * (y * 0.69)) + (z * 0.123)
        j = i.sum()
        print(j.numpy())
