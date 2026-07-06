import typing as ta


##


def is_simple_generic_alias_type(oty: type) -> bool:
    return (
        oty is ta._GenericAlias or  # type: ignore  # noqa
        oty is ta.GenericAlias  # type: ignore  # noqa
    )


##


def get_orig_bases(obj: ta.Any) -> ta.Any:
    return obj.__orig_bases__  # noqa


def get_orig_class(obj: ta.Any) -> ta.Any:
    return obj.__orig_class__  # noqa
