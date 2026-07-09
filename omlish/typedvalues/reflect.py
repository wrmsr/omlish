import typing as ta

from .. import check
from .. import lang
from .. import reflect2 as rfl
from .values import TypedValue


##


def reflect_typed_values_impls(
        *in_tys: object,
        find_abstract_subclasses: bool = False,
        get_unsealed_subclasses: ta.Callable[[type], ta.Sequence[type]] | None = None,
        mirror: rfl.Mirror | None = None,
) -> set[type[TypedValue]]:
    def get_mirror() -> rfl.Mirror:
        nonlocal mirror
        if mirror is None:
            mirror = rfl.or_global_mirror(None)
        return mirror

    tv_cls_set: set[type[TypedValue]] = set()

    todo: list[rfl.Type] = [
        in_ty if isinstance(in_ty, rfl.Type) else get_mirror().reflect_type(in_ty)
        for in_ty in in_tys
    ]

    seen: set[rfl.Type] = set()
    while todo:
        cur = todo.pop()
        if cur in seen:
            continue
        seen.add(cur)

        if isinstance(cur, rfl.UnionType):
            todo.extend(cur.items)

        elif isinstance(cur, rfl.TypeVarType):
            todo.append(cur.upper_bound)

        elif isinstance(cur, rfl.Instance):
            tv_ty: type[TypedValue] = check.issubclass(
                check.isinstance(cur.type.runtime_object, type),  # noqa
                TypedValue,
            )

            if find_abstract_subclasses and lang.is_abstract_class(tv_ty):
                if issubclass(tv_ty, lang.Sealed):
                    todo.extend([
                        get_mirror().reflect_type(nxt_ty)
                        for nxt_ty in lang.deep_subclasses(tv_ty, concrete_only=True)
                    ])

                elif get_unsealed_subclasses is not None:
                    todo.extend([
                        get_mirror().reflect_type(nxt_ty)
                        for nxt_ty in get_unsealed_subclasses(tv_ty)
                    ])

                else:
                    raise TypeError(f'{tv_ty} is not sealed - cannot safely know all subtypes')

            else:
                tv_cls_set.add(tv_ty)

        else:
            raise TypeError(cur)

    return tv_cls_set
