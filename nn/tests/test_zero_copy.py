# from ..helpers import CI
import time
import unittest

from .. import Device
from .. import Tensor


def time_tensor_numpy(out: Tensor):
    times = []
    for _ in range(5):
        st = time.perf_counter()
        out.lazydata.realized.toCPU()
        et = time.perf_counter() - st
        times.append(et)
    return min(times)


N = 4096


class TestZeroCopy(unittest.TestCase):
    @unittest.skipIf(
        Device.DEFAULT not in {"CLANG", "LLVM", "CPU", "METAL"},
        "device isn't zero copy",
    )
    def test_zero_copy_from_default_to_cpu(self):
        demo = Tensor.rand(1).realize()
        t1 = time_tensor_numpy(demo)
        out = Tensor.rand(N, N).realize()
        t2 = time_tensor_numpy(out)
        gbps = out.nbytes() * 1e-9 / max(t2 - t1, 1e-10)
        print(
            f"time(base): {t1*1e3:.2f} ms, time(copy): {t2*1e3:.2f} ms :  copy speed {gbps:.2f} GB/s"
        )
        self.assertGreater(gbps, 1000)  # more than 1000 GB/s = no copy


if __name__ == "__main__":
    unittest.main(verbosity=2)
