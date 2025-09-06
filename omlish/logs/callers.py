# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import io
import os.path
import sys
import traceback
import types
import typing as ta

from .infos import logging_context_info


##


@logging_context_info
@ta.final
class LoggingCaller(ta.NamedTuple):
    file_path: str
    line_no: int
    name: str
    stack_info: ta.Optional[str]

    @classmethod
    def is_internal_frame(cls, frame: types.FrameType) -> bool:
        file_path = os.path.normcase(frame.f_code.co_filename)

        # Yes, really.
        # https://github.com/python/cpython/blob/e709361fc87d0d9ab9c58033a0a7f2fef0ad43d2/Lib/logging/__init__.py#L204
        # https://github.com/python/cpython/commit/5ca6d7469be53960843df39bb900e9c3359f127f
        if 'importlib' in file_path and '_bootstrap' in file_path:
            return True

        return False

    @classmethod
    def find_frame(cls, ofs: int = 0) -> ta.Optional[types.FrameType]:
        f: ta.Optional[types.FrameType] = sys._getframe(2 + ofs)  # noqa

        while f is not None:
            # NOTE: We don't check __file__ like stdlib since we may be running amalgamated - we rely on careful, manual
            # stack_offset management.
            if hasattr(f, 'f_code'):
                return f

            f = f.f_back

        return None

    @classmethod
    def find(
            cls,
            ofs: int = 0,
            *,
            stack_info: bool = False,
    ) -> ta.Optional['LoggingCaller']:
        if (f := cls.find_frame(ofs + 1)) is None:
            return None

        # https://github.com/python/cpython/blob/08e9794517063c8cd92c48714071b1d3c60b71bd/Lib/logging/__init__.py#L1616-L1623  # noqa
        sinfo = None
        if stack_info:
            sio = io.StringIO()
            traceback.print_stack(f, file=sio)
            sinfo = sio.getvalue()
            sio.close()
            if sinfo[-1] == '\n':
                sinfo = sinfo[:-1]

        return cls(
            file_path=f.f_code.co_filename,
            line_no=f.f_lineno or 0,
            name=f.f_code.co_name,
            stack_info=sinfo,
        )
