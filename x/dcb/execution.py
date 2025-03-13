"""
TODO:
 - 'setup' locals - for FrozenGenerator's `condition += ' or name in {' + ', '.join(repr(f.name) for f in fields) + '}'`
   allow for `condition += ' or name in {fields_frozenset_ident}' with fields_frozenset_ident setup in preamble
"""
import types
import typing as ta

from .idents import CLS_IDENT
from .idents import FN_GLOBALS
from .ops import AddMethodOp
from .ops import AddPropertyOp
from .ops import Op
from .ops import OpRef
from .ops import OpRefMap
from .ops import SetAttrOp
from .utils import repr_round_trip_value


T = ta.TypeVar('T')


##


class OpExecutor:
    def __init__(self, cls: type, orm: OpRefMap) -> None:
        super().__init__()

        self._cls = cls
        self._orm = orm

    #

    def _create_fn(
            self,
            name: str,
            src: str,
            refs: ta.Iterable[OpRef] = (),
    ) -> types.FunctionType:
        ns = {
            CLS_IDENT: self._cls,
            **FN_GLOBALS,
        }
        for r in refs:
            ns[r.ident()] = self._orm[r]
        exec(src, ns)
        fn = ns[name]
        if not isinstance(fn, types.FunctionType):
            raise TypeError(fn)
        return fn

    def _create_opt_fn(
            self,
            name: str,
            src: str | None,
            *args: ta.Any,
            **kwargs: ta.Any,
    ) -> types.FunctionType | None:
        if src is None:
            return None

        return self._create_fn(
            name,
            src,
            *args,
            **kwargs,
        )

    #

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
            if isinstance(v := op.value, OpRef):
                v = self._orm[v]
                if isinstance(v, types.FunctionType):
                    v.__qualname__ = f'{self._cls.__qualname__}.{v.__name__}'
            else:
                v = repr_round_trip_value(v)
            setattr(self._cls, op.name, v)

        elif isinstance(op, AddMethodOp):
            if op.name in self._cls.__dict__:
                raise AttributeError(op.name)
            fn = self._create_fn(
                op.name,
                op.src,
                op.refs,
            )
            fn.__qualname__ = f'{self._cls.__qualname__}.{op.name}'
            setattr(self._cls, op.name, fn)

        elif isinstance(op, AddPropertyOp):
            get_fn = self._create_opt_fn(
                op.name,
                op.get_src,
                op.refs,
            )
            set_fn = self._create_opt_fn(
                op.name,
                op.set_src,
                op.refs,
            )
            del_fn = self._create_opt_fn(
                op.name,
                op.del_src,
                op.refs,
            )
            prop = property(
                get_fn,
                set_fn,
                del_fn,
            )
            setattr(self._cls, op.name, prop)

        else:
            raise TypeError(op)
