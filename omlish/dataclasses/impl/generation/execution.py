"""
TODO:
 - 'setup' locals - for FrozenGenerator's `condition += ' or name in {' + ', '.join(repr(f.name) for f in fields) + '}'`
   allow for `condition += ' or name in {fields_frozenset_ident}' with fields_frozenset_ident setup in preamble
"""
import sys
import types
import typing as ta

from .... import lang
from ..utils import repr_round_trip_value
from .globals import FN_GLOBAL_VALUES
from .globals import FnGlobal
from .idents import CLS_IDENT
from .ops import AddMethodOp
from .ops import AddPropertyOp
from .ops import IfAttrPresent
from .ops import Op
from .ops import OpRef
from .ops import OpRefMap
from .ops import Ref
from .ops import SetAttrOp


T = ta.TypeVar('T')


##


class OpExecutor:
    def __init__(self, cls: type, orm: OpRefMap) -> None:
        super().__init__()

        self._cls = cls
        self._orm = orm

    #

    @lang.cached_function(no_wrapper_update=True)
    def _cls_globals(self) -> dict[str, ta.Any]:
        if self._cls.__module__ in sys.modules:
            return sys.modules[self._cls.__module__].__dict__
        else:
            return {}

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
            refs: ta.Iterable[Ref] = (),
    ) -> types.FunctionType:
        lo: dict = {
            CLS_IDENT: self._cls,
            **FN_GLOBAL_VALUES,
        }
        for r in refs:
            if isinstance(r, OpRef):
                lo[r.ident()] = self._orm[r]
            elif isinstance(r, FnGlobal):
                pass
            else:
                raise TypeError(r)

        x_src = '\n'.join([
            f'def __create_fn__(',
            f'    *,',
            *[
                f'    {k},'
                for k in lo
            ],
            f'):',
            *[
                f'    {l}'
                for l in src.splitlines()
            ],
            f'',
            f'    return {name}',
        ])

        ns: dict = {}
        exec(
            x_src,
            self._cls_globals(),
            ns,
        )
        x_fn = ns['__create_fn__']
        fn = x_fn(**lo)

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
