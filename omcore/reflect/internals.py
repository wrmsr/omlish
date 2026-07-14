"""
As with `omcore.dataclasses._internals` this is a place for centralizing access to `typing` internals (which have a
history of changing significantly between python versions).
"""
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
