import typing as ta

from omlish import lang
from omlish.dev import pytest as ptu

if ta.TYPE_CHECKING:
    import pyopencl
else:
    pyopencl = lang.proxy_import('pyopencl')


@ptu.skip_if_cant_import('pyopencl')
def test_opencl():
    pass
