import types
import typing as ta

from .idents import CLS_IDENT
from .idents import FN_GLOBALS
from .ops import AddMethodOp
from .ops import Op
from .ops import OpRefMap
from .ops import SetAttrOp


T = ta.TypeVar('T')


##


def set_qualname(cls: type, value: T) -> T:
    if isinstance(value, types.FunctionType):
        value.__qualname__ = f'{cls.__qualname__}.{value.__name__}'
    return value


class OpExecutor:
    def __init__(self, cls: type, orm: OpRefMap) -> None:
        super().__init__()

        self._cls = cls
        self._orm = orm

    def execute(self, op: Op) -> None:
        if isinstance(op, SetAttrOp):
            if op.name in self._cls.__dict__:
                if op.if_present == 'skip':
                    return
                elif op.if_present == 'replace':
                    pass
                elif op.if_present == 'raise':
                    raise AttributeError(op.name)
                else:
                    raise ValueError(op.if_present)
            set_qualname(self._cls, op.value)
            setattr(self._cls, op.name, op.value)

        elif isinstance(op, AddMethodOp):
            if op.name in self._cls.__dict__:
                raise AttributeError(op.name)
            ns = {
                CLS_IDENT: self._cls,
                **FN_GLOBALS,
            }
            for r in op.refs:
                ns[r.ident()] = self._orm[r]
            exec(op.src, ns)
            fn = ns[op.name]
            set_qualname(self._cls, fn)
            setattr(self._cls, op.name, fn)

        else:
            raise TypeError(op)
