import typing as ta


IfAttrPresent: ta.TypeAlias = ta.Literal['skip', 'replace', 'raise']


##


def set_cls_attr(
        cls: type,
        attr_name: str,
        value: ta.Any,
        if_present: IfAttrPresent,
        *,
        set_qualname: bool = False,
) -> None:
    if attr_name in cls.__dict__:
        if if_present == 'skip':
            return
        elif if_present == 'replace':
            pass
        elif if_present == 'raise':
            raise TypeError(f'Cannot overwrite attribute {attr_name} in class {cls.__name__}')
        else:
            raise ValueError(if_present)

    if set_qualname:
        value.__qualname__ = f'{cls.__qualname__}.{attr_name}'

    setattr(cls, attr_name, value)

    return
