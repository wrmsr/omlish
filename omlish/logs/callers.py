# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import io
import os.path
import sys
import traceback
import types
import typing as ta


##


class LoggingCaller(ta.NamedTuple):
    filename: str
    lineno: int
    func: str
    sinfo: ta.Optional[str]

    @classmethod
    def is_internal_frame(cls, frame: types.FrameType) -> bool:
        filename = os.path.normcase(frame.f_code.co_filename)

        # https://github.com/python/cpython/commit/5ca6d7469be53960843df39bb900e9c3359f127f
        if 'importlib' in filename and '_bootstrap' in filename:
            return True

        return False

    @classmethod
    def find_frame(cls, ofs: int = 0) -> types.FrameType:
        f: ta.Optional[types.FrameType] = sys._getframe(2 + ofs)  # noqa

        while f is not None:
            if hasattr(f, 'f_code'):
                return f

            f = f.f_back

        raise RuntimeError

    @classmethod
    def find(
            cls,
            ofs: int = 0,
            *,
            stack_info: bool = False,
    ) -> 'LoggingCaller':
        f = cls.find_frame(ofs + 1)
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
