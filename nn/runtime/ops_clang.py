import ctypes
import functools
import pathlib
import platform
import subprocess
import tempfile
import time
import typing as ta

from ..codegen.kernel import LinearizerOptions
from ..execution import Compiled
from ..helpers import diskcache
from ..renderer.cstyle import CStyleLanguage
from ..renderer.cstyle import uops_to_cstyle
from ..runtime.lib import RawMallocBuffer


args = {
    'Linux': {'cflags': '-lm -fPIC --rtlib=compiler-rt ', 'ext': 'so'},
    'Darwin': {'cflags': '-lm -fPIC --rtlib=compiler-rt ', 'ext': 'dylib'}
}[platform.system()]


CLANG_PROGRAM_HEADER = """
#include <math.h>
#define max(x,y) ((x>y)?x:y)
#define int64 long
#define half __fp16
#define uchar unsigned char
#include <stdbool.h>
"""


@diskcache
def compile_clang(prg: str, header: str = CLANG_PROGRAM_HEADER) -> bytes:
    # TODO: remove file write. sadly clang doesn't like the use of /dev/stdout here
    with tempfile.NamedTemporaryFile(delete=True) as output_file:
        subprocess.check_output(
            args=(
                    'clang '
                    '-shared '
                    '-O2 '
                    '-Wall '
                    '-Werror '
                    '-x c ' + args['cflags'] +
                    ' - '
                    '-o ' + str(output_file.name)).split(),
            input=(header + prg).encode('utf-8'),
        )
        return pathlib.Path(output_file.name).read_bytes()


class ClangProgram:
    def __init__(self, name: str, prg: str) -> None:
        # write to disk so we can load it
        with tempfile.NamedTemporaryFile(delete=True) as cached_file_path:
            pathlib.Path(cached_file_path.name).write_bytes(prg)
            self.fxn: ta.Any = ctypes.CDLL(str(cached_file_path.name))[name]

    def __call__(self, unused_global_size, unused_local_size, *args, wait=False):
        if wait:
            st = time.perf_counter()
        self.fxn(*[x._buf if isinstance(x, RawMallocBuffer) else x for x in args])
        if wait:
            return time.perf_counter() - st


renderer = functools.partial(
    uops_to_cstyle,
    CStyleLanguage(
        buffer_suffix=" restrict",
        arg_int_prefix="const int",
    ),
)


ClangBuffer = Compiled(
    RawMallocBuffer,
    LinearizerOptions(
        supports_float4=False,
        has_local=False,
    ),
    renderer,
    compile_clang,
    ClangProgram,
)
