import typing as ta

from .globals import OBJECT_SETATTR_GLOBAL
from .globals import FnGlobal
from .idents import SELF_DICT_IDENT
from .idents import SELF_IDENT


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
    def __init__(
            self,
            *,
            object_ident: str = SELF_IDENT,
            object_dict_ident: str | None = None,
    ) -> None:
        super().__init__()

        self._object_ident = object_ident
        self._object_dict_ident = object_dict_ident

        self._has_set_object_dict = False
        self._global_refs: set[FnGlobal] = set()

    @property
    def refs(self) -> ta.AbstractSet[FnGlobal]:
        return self._global_refs

    def __call__(
            self,
            name: str,
            value_src: str,
            *,
            frozen: bool,
            override: bool,
    ) -> list[str]:
        if override:
            if self._object_dict_ident is not None:
                return [f'{self._object_dict_ident}[{name!r}] = {value_src}']

            else:
                if not self._has_set_object_dict:
                    x = [
                        f'{SELF_DICT_IDENT} = {self._object_ident}.__dict__',
                    ]
                    self._has_set_object_dict = True
                else:
                    x = []
                return [
                    *x,
                    f'{SELF_DICT_IDENT}[{name!r}] = {value_src}',
                ]

        elif frozen:
            self._global_refs.add(OBJECT_SETATTR_GLOBAL)
            return [f'{OBJECT_SETATTR_GLOBAL.ident}({self._object_ident}, {name!r}, {value_src})']

        else:
            return [f'{self._object_ident}.{name} = {value_src}']
