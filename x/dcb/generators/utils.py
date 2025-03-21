from ..idents import OBJECT_SETATTR_IDENT
from ..idents import SELF_DICT_IDENT
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


class SetattrSrcBuilder:
    def __init__(self) -> None:
        super().__init__()

        self._has_set_self_dict = False

    def __call__(
            self,
            name: str,
            value_src: str,
            *,
            frozen: bool,
            override: bool,

            object_ident: str = SELF_IDENT,
            object_dict_ident: str | None = None,
    ) -> list[str]:
        if override:
            if object_dict_ident is not None:
                return [f'{object_dict_ident}[{name!r}] = {value_src}']

            else:
                if not self._has_set_self_dict:
                    x = [
                        f'{SELF_DICT_IDENT} = {object_ident}.__dict__',
                    ]
                    self._has_set_self_dict = True
                else:
                    x = []
                return [
                    *x,
                    f'{SELF_DICT_IDENT}[{name!r}] = {value_src}',
                ]

        elif frozen:
            return [f'{OBJECT_SETATTR_IDENT}({object_ident}, {name!r}, {value_src})']

        else:
            return [f'{object_ident}.{name} = {value_src}']
