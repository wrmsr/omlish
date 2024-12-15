import typing as ta


def pypprint(*args: ta.Any, **kwargs: ta.Any) -> None:
    """
    Replacement for ``print`` that special-cases dicts and iterables.

    - Dictionaries are printed one line per key-value pair, with key and value colon-separated.
    - Iterables (excluding strings) are printed one line per item
    - Everything else is delegated to ``print``
    """

    if len(args) != 1:
        print(*args, **kwargs)
        return
    x = args[0]
    if isinstance(x, dict):
        for k, v in x.items():
            print(f'{k}:', v, **kwargs)
    elif isinstance(x, ta.Iterable) and not isinstance(x, str):
        for i in x:
            print(i, **kwargs)
    else:
        print(x, **kwargs)
