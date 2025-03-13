from ..idents import OBJECT_SETATTR_IDENT
from ..idents import SELF_IDENT


##


def build_attr_tuple_src(obj_name: str, *attrs: str) -> str:
    if not attrs:
        return '()'

    return f'({", ".join([f"{obj_name}.{a}" for a in attrs])}{"," if len(attrs) < 2 else ""})'


def build_attr_kwargs_src(obj_name: str, *attrs: str) -> str:
    return ', '.join([f'{a}={obj_name}.{a}' for a in attrs])


def build_setattr_src(
        name: str,
        value_src: str,
        *,
        frozen: bool,
        override: bool,

        object_ident: str = SELF_IDENT,
) -> str:
    if override:
        return f'{object_ident}.__dict__[{name!r}] = {value_src}'
    elif frozen:
        return f'{OBJECT_SETATTR_IDENT}({object_ident}, {name!r}, {value_src})'
    else:
        return f'{object_ident}.{name} = {value_src}'
