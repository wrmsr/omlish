import typing as ta

from omcore import check
from omcore import collections as col


##


class TypeTagged:
    __type_tag_field__: str
    __type_tag__: str

    def __init_subclass__(
            cls,
            *,
            type_tag_field: str | None = None,
            type_tag: str | None = None,
            **kwargs: ta.Any,
    ) -> None:
        super().__init_subclass__(**kwargs)

        if tt_atts := {a for a in cls.__dict__ if a.startswith('__type_tag') and a.endswith('__')}:
            raise TypeError(f'Must not manually set type tagging attributes: {tt_atts}')

        tt_fs, tt_vs = [
            col.multi_map((
                (getattr(bc, a), bc)
                for bc in cls.__bases__
                if hasattr(bc, a)
            ))
            for a in ['__type_tag_field__', '__type_tag__']
        ]

        if tt_fs:
            check.single(tt_fs)
            check.none(type_tag_field)
        elif type_tag_field is not None:
            cls.__type_tag_field__ = check.non_empty_str(type_tag_field)

        if tt_vs:
            check.single(tt_vs)
            check.none(type_tag)
        elif type_tag is not None:
            cls.__type_tag__ = check.non_empty_str(type_tag)
