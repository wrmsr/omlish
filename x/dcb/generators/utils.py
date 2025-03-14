from ..idents import OBJECT_SETATTR_IDENT
from ..idents import SELF_IDENT


##


def build_attr_tuple_body_src_lines(
        obj_name: str,
        *attrs: str,
        prefix: str = '',
) -> list[str]:
    return [
        f'{prefix}{obj_name}.{a},'
        for a in attrs
    ]


def build_attr_kwargs_body_src_lines(
        obj_name: str,
        *attrs: str,
        prefix: str = '',
) -> list[str]:
    return [
        f'{prefix}{a}={obj_name}.{a},'
        for a in attrs
    ]


def build_setattr_src(
        name: str,
        value_src: str,
        *,
        frozen: bool,
        override: bool,

        object_ident: str = SELF_IDENT,
        object_dict_ident: str | None = None,
) -> str:
    if override:
        if object_dict_ident is not None:
            return f'{object_dict_ident}[{name!r}] = {value_src}'
        else:
            return f'{object_ident}.__dict__[{name!r}] = {value_src}'
    elif frozen:
        return f'{OBJECT_SETATTR_IDENT}({object_ident}, {name!r}, {value_src})'
    else:
        return f'{object_ident}.{name} = {value_src}'
