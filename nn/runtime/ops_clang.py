import ctypes
import functools
import pathlib
import subprocess
import tempfile
from typing import Any

from ..codegen.kernel import LinearizerOptions
from ..device import Compiled
from ..device import MallocAllocator
from ..helpers import cpu_time_execution
from ..helpers import diskcache
from ..renderer.cstyle import CStyleLanguage
from ..renderer.cstyle import uops_to_cstyle

CLANG_PROGRAM_HEADER = "#include <math.h>\n#define max(x,y) ((x>y)?x:y)\n#define int64 long\n#define half __fp16\n#define uchar unsigned char\n#include <stdbool.h>\n"  # noqa: E501


@diskcache
def compile_clang(prg: str, header: str = CLANG_PROGRAM_HEADER) -> bytes:
    # TODO: remove file write. sadly clang doesn't like the use of /dev/stdout here
    with tempfile.NamedTemporaryFile(delete=True) as output_file:
        subprocess.check_output(
            args=(
                "clang -shared -march=native -O2 -Wall -Werror -x c -fPIC - -o "
                + str(output_file.name)
            ).split(),
            input=(header + prg).encode("utf-8"),
        )  # noqa: E501
        return pathlib.Path(output_file.name).read_bytes()


class ClangProgram:
    def __init__(self, name: str, lib: bytes):
        self.name, self.lib = name, lib
        # write to disk so we can load it
        with tempfile.NamedTemporaryFile(delete=True) as cached_file_path:
            pathlib.Path(cached_file_path.name).write_bytes(lib)
            self.fxn: Any = ctypes.CDLL(str(cached_file_path.name))[name]

    def __call__(self, *bufs, vals=(), wait=False):
        return cpu_time_execution(lambda: self.fxn(*bufs, *vals), enable=wait)


renderer = functools.partial(
    uops_to_cstyle,
    CStyleLanguage(buffer_suffix=" restrict"),
)
ClangDevice = Compiled(
    MallocAllocator,
    LinearizerOptions(supports_float4=False, has_local=False),
    renderer,
    compile_clang,
    ClangProgram,
)
