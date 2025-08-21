import importlib.util
import types
import typing as ta


##


def lazy_import(
        name: str,
        package: str | None = None,
        *,
        optional: bool = False,
        cache_failure: bool = False,
) -> ta.Callable[[], ta.Any]:
    result = not_set = object()

    def inner():
        nonlocal result

        if result is not not_set:
            if isinstance(result, Exception):
                raise result
            return result

        try:
            mod = importlib.import_module(name, package=package)

        except Exception as e:
            if optional:
                if cache_failure:
                    result = None
                return None

            if cache_failure:
                result = e
            raise

        result = mod
        return mod

    return inner


def proxy_import(
        name: str,
        package: str | None = None,
        extras: ta.Iterable[str] | None = None,
) -> types.ModuleType:
    if isinstance(extras, str):
        raise TypeError(extras)

    omod = None

    def __getattr__(att):  # noqa
        nonlocal omod
        if omod is None:
            omod = importlib.import_module(name, package=package)
            if extras:
                for x in extras:
                    importlib.import_module(f'{name}.{x}', package=package)
        return getattr(omod, att)

    lmod = types.ModuleType(name)
    lmod.__getattr__ = __getattr__  # type: ignore[method-assign]
    return lmod
