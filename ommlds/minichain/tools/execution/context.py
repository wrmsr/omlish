import contextlib
import contextvars
import typing as ta

from omlish import collections as col
from omlish import dataclasses as dc
from omlish import lang


T = ta.TypeVar('T')


##


@dc.dataclass(frozen=True)
class ToolContext(lang.Final):
    dct: col.TypeMap = col.TypeMap()

    @classmethod
    def new(cls, *objs: ta.Any) -> 'ToolContext':
        return cls(col.TypeMap(objs))

    #

    def __len__(self) -> int:
        return len(self.dct)

    def __iter__(self) -> ta.Iterator[ta.Any]:
        return iter(self.dct)

    def get(self, ty: type[T]) -> T | None:
        return self.dct.get(ty)

    def __getitem__(self, cls: type[T]) -> T:
        return self.dct[cls]

    def get_any(self, cls: type | tuple[type, ...]) -> ta.Sequence[T]:
        return self.dct.get_any(cls)


##


_TOOL_CONTEXT: contextvars.ContextVar[ToolContext] = contextvars.ContextVar(f'{__name__}._TOOL_CONTEXT')


@contextlib.contextmanager
def bind_tool_context(ctx: ToolContext) -> ta.Generator[ToolContext]:
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
