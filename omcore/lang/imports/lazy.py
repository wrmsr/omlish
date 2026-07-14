import importlib.util
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
