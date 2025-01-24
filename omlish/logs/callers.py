# ruff: noqa: UP006 UP007
# @omlish-lite
import io
import sys
import traceback
import types
import typing as ta


class LoggingCaller(ta.NamedTuple):
    filename: str
    lineno: int
    func: str
    sinfo: ta.Optional[str]

    @classmethod
    def find_frame(cls, ofs: int = 0) -> types.FrameType:
        f: ta.Any = sys._getframe(2 + ofs)  # noqa
        while hasattr(f, 'f_code'):
            if f.f_code.co_filename != __file__:
                return f
            f = f.f_back
        raise RuntimeError

    @classmethod
    def find(cls, stack_info: bool = False) -> 'LoggingCaller':
        f = cls.find_frame(1)
        # TODO: ('(unknown file)', 0, '(unknown function)', None) ?

        sinfo = None
        if stack_info:
            sio = io.StringIO()
            sio.write('Stack (most recent call last):\n')
            traceback.print_stack(f, file=sio)
            sinfo = sio.getvalue()
            sio.close()
            if sinfo[-1] == '\n':
                sinfo = sinfo[:-1]

        return cls(
            f.f_code.co_filename,
            f.f_lineno,
            f.f_code.co_name,
            sinfo,
        )
