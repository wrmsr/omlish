import typing as ta


##


class TypeTagged:
    def __init_subclass__(
            cls,
            *,
            type_tag_field: str | None = None,
            type_tag: str | None = None,
            **kwargs: ta.Any,
    ) -> None:
        super().__init_subclass__(**kwargs)
