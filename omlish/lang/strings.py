def camel_case(name: str) -> str:
    return ''.join(map(str.capitalize, name.split('_')))


def snake_case(name: str) -> str:
    uppers: list[int | None] = [i for i, c in enumerate(name) if c.isupper()]
    return '_'.join([name[l:r].lower() for l, r in zip([None] + uppers, uppers + [None])]).strip('_')
