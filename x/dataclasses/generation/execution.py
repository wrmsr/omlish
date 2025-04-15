"""
TODO:
 - 'setup' locals - for FrozenGenerator's `condition += ' or name in {' + ', '.join(repr(f.name) for f in fields) + '}'`
   allow for `condition += ' or name in {fields_frozenset_ident}' with fields_frozenset_ident setup in preamble
"""
import types
import typing as ta

from ..utils import repr_round_trip_value
from .idents import CLS_IDENT
from .idents import FN_GLOBAL_VALUES
from .ops import AddMethodOp
from .ops import AddPropertyOp
from .ops import IfAttrPresent
from .ops import Op
from .ops import OpRef
from .ops import OpRefMap
from .ops import SetAttrOp


T = ta.TypeVar('T')


##


class OpExecutor:
    def __init__(self, cls: type, orm: OpRefMap) -> None:
        super().__init__()

        self._cls = cls
        self._orm = orm

    #

    def _set_fn_qualname(self, fn: types.FunctionType, name: str | None = None) -> types.FunctionType:
        if name is None:
            name = fn.__name__
        fn.__qualname__ = f'{self._cls.__qualname__}.{name}'
        return fn

    def _create_fn(
            self,
            name: str,
            src: str,
            refs: ta.Iterable[OpRef] = (),
    ) -> types.FunctionType:
        ns: dict = {
            CLS_IDENT: self._cls,
            **FN_GLOBAL_VALUES,
        }
        for r in refs:
            ns[r.ident()] = self._orm[r]

        exec(src, ns)
        fn = ns[name]

        if not isinstance(fn, types.FunctionType):
            raise TypeError(fn)

        self._set_fn_qualname(fn, name)

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

    def _execute_set_attr(
            self,
            attr_name: str,
            value: ta.Any,
            if_present: IfAttrPresent,
    ) -> None:
        if attr_name in self._cls.__dict__:
            if if_present == 'skip':
                return
            elif if_present == 'replace':
                pass
            elif if_present == 'error':
                raise TypeError(f'Cannot overwrite attribute {attr_name} in class {self._cls.__name__}')
            else:
                raise ValueError(if_present)

        setattr(self._cls, attr_name, value)

    def execute(self, op: Op) -> None:
        if isinstance(op, SetAttrOp):
            if isinstance(v := op.value, OpRef):
                v = self._orm[v]
                if isinstance(v, types.FunctionType):
                    self._set_fn_qualname(v)
            else:
                v = repr_round_trip_value(v)

            self._execute_set_attr(
                op.name,
                v,
                op.if_present,
            )

        elif isinstance(op, AddMethodOp):
            fn = self._create_fn(
                op.name,
                op.src,
                op.refs,
            )

            self._execute_set_attr(
                op.name,
                fn,
                op.if_present,
            )

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
