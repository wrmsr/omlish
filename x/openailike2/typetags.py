import typing as ta


##


class TypeTagged:
    __type_tag_field__: str
    __type_tag__: str

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)
