import mmap
import os
import typing as ta

try:
    import _posixshmem
except Exception:
    pass

from .. import ops
from ..dtypes import DType
from ..execution import Interpreted
from ..helpers import OSX
from ..helpers import all_int
from ..helpers import prod
from ..runtime.lib import RawBufferMapped
from ..shape.view import strides_for_shape


MAP_LOCKED = 0x2000
MAP_POPULATE = 0x008000


class UnderlyingDiskBuffer:
    def __init__(self, fd, mem):
        super().__init__()
        self.fd = fd
        self.mem = mem

    def __del__(self):
        if self.fd:
            self.fd.close()


class RawDiskBuffer(RawBufferMapped):
    def __init__(
            self,
            size,
            dtype: DType,
            buf=None,
            device: ta.Optional[str] = None,
            offset: int = 0,
    ) -> None:  # pylint: disable=super-init-not-called
        # super *not* called

        assert (
                device is not None or buf is not None
        ), "disk tensor needs a path or a buf"

        if device is not None:
            if str(device).startswith("shm:"):
                if OSX:
                    with open(f"/tmp/shm_{device[4:]}", "w+b") as f:
                        f.truncate(size * dtype.itemsize)
                        shm = mmap.mmap(f.fileno(), size * dtype.itemsize, flags=mmap.MAP_SHARED)

                else:
                    fd = _posixshmem.shm_open(device[4:], os.O_RDWR, 0o600)
                    # TODO: these flags are somewhat platform specific, but python doesn't expose the ones we need
                    shm = mmap.mmap(fd, size * dtype.itemsize, flags=mmap.MAP_SHARED | MAP_LOCKED | MAP_POPULATE)
                    shm.madvise(mmap.MADV_HUGEPAGE)  # type: ignore   # not on OSX
                    os.close(fd)
                buf = UnderlyingDiskBuffer(None, shm)

            else:
                f = open(device, "a+b")
                if os.path.getsize(device) < size * dtype.itemsize:
                    os.ftruncate(f.fileno(), size * dtype.itemsize)
                buf = UnderlyingDiskBuffer(f, mmap.mmap(f.fileno(), size * dtype.itemsize))

        # NOTE: we don't call super since disk tensors don't use RAM
        self.size = size
        self.dtype = dtype
        self._buf = buf
        self.offset = offset

    def cast(self, arg: tuple[DType, bool]):
        return RawDiskBuffer(self.size, arg[0], self._buf, offset=self.offset)

    def as_strided(self, arg):
        assert strides_for_shape(arg[0]) == arg[1], "disk tensors don't support strides"
        return RawDiskBuffer(prod(arg[0]), self.dtype, self._buf, offset=self.offset + arg[2] * self.dtype.itemsize)

    def _buffer(self):
        return memoryview(self._buf.mem)[self.offset:self.offset + self.size * self.dtype.itemsize]

    def readinto(self, buf: memoryview):
        if self._buf.fd is not None:
            self._buf.fd.seek(self.offset)
            self._buf.fd.readinto(buf)
        else:
            buf.cast('B')[:] = self._buffer()

    def transfer(self, cls, shape, dtype, **kwargs):
        assert all_int(shape), "does not support symbolic shape"
        instance = cls(prod(shape), dtype, **kwargs)
        self.readinto(instance._buffer())
        return instance


disk_fxn_for_op: dict[type[ops.LazyOp], ta.Callable] = {
    ops.Mem: lambda x: x,
    ops.Nop: lambda x: x,
    ops.Cast: RawDiskBuffer.cast,
    ops.AsStrided: RawDiskBuffer.as_strided,
}


DiskBuffer = Interpreted(
    RawDiskBuffer,
    disk_fxn_for_op,
)
