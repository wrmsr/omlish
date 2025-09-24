import contextlib
import contextvars
import typing as ta

from omlish import check
from omlish import collections as col
from omlish import lang


T = ta.TypeVar('T')


##


class ToolContext(lang.Final):
    def __init__(self, *items: ta.Any) -> None:
        super().__init__()

        self._dct: col.TypeMap = col.TypeMap(items)
        if ToolContext in self._dct:
            raise KeyError(ToolContext)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}<{", ".join(ic.__name__ for ic in self._dct)}>'

    def __len__(self) -> int:
        return len(self._dct)

    def __iter__(self) -> ta.Iterator[ta.Any]:
        return iter(self._dct)

    def __contains__(self, ty: type[T]) -> bool:
        return ty in self._dct

    def get(self, ty: type[T]) -> T | None:
        return self._dct.get(ty)

    def __getitem__(self, cls: type[T]) -> T:
        return self._dct[cls]

    def get_any(self, cls: type | tuple[type, ...]) -> ta.Sequence[T]:
        return self._dct.get_any(cls)


##


_TOOL_CONTEXT: contextvars.ContextVar[ToolContext] = contextvars.ContextVar(f'{__name__}._TOOL_CONTEXT')


@ta.overload
def bind_tool_context(ctx: ToolContext) -> ta.ContextManager[ToolContext]:
    ...


@ta.overload
def bind_tool_context(*items: ta.Any) -> ta.ContextManager[ToolContext]:
    ...


@contextlib.contextmanager  # type: ignore[misc]
def bind_tool_context(*args):
    if args and isinstance(args[0], ToolContext):
        check.arg(len(args) == 1)
        ctx = args[0]
    else:
        ctx = ToolContext(*args)

    try:
        cur = _TOOL_CONTEXT.get()
    except LookupError:
        pass
    else:
        raise RuntimeError(f'Already bound: {cur}')

    tok = _TOOL_CONTEXT.set(ctx)
    try:
        yield ctx
    finally:
        _TOOL_CONTEXT.reset(tok)


def tool_context() -> ToolContext:
    return _TOOL_CONTEXT.get()
