import typing as ta


##


def enum_name_repr(e: ta.Any) -> str:
    return f'{e.__class__.__name__}.{e.name}'
