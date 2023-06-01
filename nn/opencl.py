import typing as ta

from omlish import lang

if ta.TYPE_CHECKING:
    import pyopencl as cl
else:
    cl = lang.proxy_import('pyopencl')

from . import evaluators
from .devices import Device
from .evaluators import Evaluator


class OpenclDevice(Device):
    @property
    def evaluator(self) -> Evaluator:
        raise NotImplementedError


# class OpenclCompiler(evaluators.Compiler):
#     def __int__(self) -> None:
#         super().__init__(
#
#         )


@lang.cached_nullary
def opencl_compiler() -> evaluators.Compiler:
    raise NotImplementedError
