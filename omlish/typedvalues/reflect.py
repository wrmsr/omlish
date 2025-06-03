import typing as ta

from .. import check
from .. import lang
from .. import reflect as rfl
from .values import TypedValue


##


def reflect_typed_values_impls(
        *rtys: rfl.Type,
        find_abstract_subclasses: bool = False,
) -> set[type[TypedValue]]:
    tv_cls_set: set[type[TypedValue]] = set()

    todo = list(rtys)
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

        elif isinstance(cur, type):
            cur = check.issubclass(check.isinstance(cur, type), TypedValue)

            if find_abstract_subclasses and lang.is_abstract_class(cur):
                todo.extend(lang.deep_subclasses(cur, concrete_only=True))

            else:
                tv_cls_set.add(cur)

        else:
            raise TypeError(cur)

    return tv_cls_set
