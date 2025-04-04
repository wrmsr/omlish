"""
FIXME:
 - macos pipe size lol, and just like checking at all
"""
import contextlib
import fcntl
import os
import tempfile
import typing as ta


##


class SubprocessFileInput(ta.NamedTuple):
    file_path: str
    pass_fds: ta.Sequence[int]


SubprocessFileInputMethod: ta.TypeAlias = ta.Callable[[bytes], ta.ContextManager[SubprocessFileInput]]


@contextlib.contextmanager
def temp_subprocess_file_input(buf: bytes) -> ta.Iterator[SubprocessFileInput]:
    with tempfile.NamedTemporaryFile(delete=True) as kf:
        kf.write(buf)
        kf.flush()
        yield SubprocessFileInput(kf.name, [])


@contextlib.contextmanager
def pipe_fd_subprocess_file_input(buf: bytes) -> ta.Iterator[SubprocessFileInput]:
    rfd, wfd = os.pipe()
    closed_wfd = False
    try:
        if hasattr(fcntl, 'F_SETPIPE_SZ'):
            fcntl.fcntl(wfd, fcntl.F_SETPIPE_SZ, max(len(buf), 0x1000))
        n = os.write(wfd, buf)
        if n != len(buf):
            raise OSError(f'Failed to write data to pipe: {n=} {len(buf)=}')
        os.close(wfd)
        closed_wfd = True
        yield SubprocessFileInput(f'/dev/fd/{rfd}', [rfd])
    finally:
        if not closed_wfd:
            os.close(wfd)
        os.close(rfd)
