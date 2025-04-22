import typing as ta

from .. import check
from .. import reflect as rfl
from .values import TypedValue


##


def reflect_typed_values_impls(rty: rfl.Type) -> set[type[TypedValue]]:
    tv_cls_set: set[type[TypedValue]] = set()

    todo = [rty]
    seen = set()
    while todo:
        cur = todo.pop()
        if cur in seen:
            continue
        seen.add(cur)

        if isinstance(cur, rfl.Union):
            todo.extend(cur.args)
        elif isinstance(cur, ta.TypeVar):
            todo.append(rfl.type_(rfl.get_type_var_bound(cur)))
        else:
            tv_cls_set.add(check.issubclass(check.isinstance(cur, type), TypedValue))

    return tv_cls_set
