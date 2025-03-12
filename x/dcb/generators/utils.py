def build_attr_tuple_str(obj_name: str, *attrs: str) -> str:
    if not attrs:
        return '()'

    return f'({", ".join([f"{obj_name}.{a}" for a in attrs])},)'


def build_attr_kwargs_str(obj_name: str, *attrs: str) -> str:
    return ', '.join([f'{a}={obj_name}.{a}' for a in attrs])
