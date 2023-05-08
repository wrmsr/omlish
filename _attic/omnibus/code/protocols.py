import sys
import typing as ta

from .. import lang


class TracebackProtocol(lang.Protocol):

    @property
    def tb_frame(self) -> 'FrameProtocol': ...

    @property
    def tb_lasti(self) -> int: ...

    @property
    def tb_lineno(self) -> ta.Optional[int]: ...

    @property
    def tb_next(self) -> ta.Optional['TracebackProtocol']: ...


class FrameProtocol(lang.Protocol):

    @property
    def f_back(self) -> ta.Optional['FrameProtocol']: ...

    @property
    def f_builtins(self): ...

    @property
    def f_code(self) -> 'CodeProtocol': ...

    @property
    def f_globals(self): ...

    @property
    def f_lasti(self) -> int: ...

    @property
    def f_lineno(self) -> ta.Optional[int]: ...

    @property
    def f_locals(self): ...

    @property
    def f_trace(self) -> ta.Optional[ta.Callable]: ...


class CodeProtocol(lang.Protocol):

    @property
    def co_argcount(self) -> int: ...

    @property
    def co_code(self) -> bytes: ...

    @property
    def co_cellvars(self) -> ta.Sequence[str]: ...

    @property
    def co_consts(self) -> ta.Sequence[ta.Any]: ...

    @property
    def co_filename(self) -> ta.Optional[str]: ...

    @property
    def co_firstlineno(self) -> ta.Optional[int]: ...

    @property
    def co_flags(self) -> int: ...

    @property
    def co_freevars(self) -> ta.Sequence[str]: ...

    if sys.version_info[1] > 7:
        @property
        def co_posonlyargcount(self) -> int: ...

    @property
    def co_kwonlyargcount(self) -> int: ...

    @property
    def co_lnotab(self): ...

    @property
    def co_name(self) -> ta.Optional[str]: ...

    @property
    def co_names(self) -> ta.Sequence[str]: ...

    @property
    def co_nlocals(self) -> int: ...

    @property
    def co_stacksize(self) -> int: ...

    @property
    def co_varnames(self) -> ta.Sequence[str]: ...
