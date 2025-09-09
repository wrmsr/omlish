import contextlib
import importlib.util
import types
import typing as ta

from .capture import ImportCapture


##


def proxy_import(
        spec: str,
        package: str | None = None,
        extras: ta.Iterable[str] | None = None,
) -> types.ModuleType:
    if isinstance(extras, str):
        raise TypeError(extras)

    omod = None

    def __getattr__(att):  # noqa
        nonlocal omod
        if omod is None:
            omod = importlib.import_module(spec, package=package)
            if extras:
                for x in extras:
                    importlib.import_module(f'{spec}.{x}', package=package)
        return getattr(omod, att)

    lmod = types.ModuleType(spec)
    lmod.__getattr__ = __getattr__  # type: ignore[method-assign]
    return lmod


##


@contextlib.contextmanager
def auto_proxy_import(
        mod_globals: ta.MutableMapping[str, ta.Any],
        *,
        disable: bool = False,

        unreferenced_callback: ta.Callable[[ta.Mapping[str, ta.Sequence[str | None]]], None] | None = None,
        raise_unreferenced: bool = False,
) -> ta.Iterator[ImportCapture]:
    inst = ImportCapture(
        mod_globals,
        disable=disable,
    )

    with inst.capture(
            unreferenced_callback=unreferenced_callback,
            raise_unreferenced=raise_unreferenced,
    ):
        yield inst

    pkg = mod_globals.get('__package__')
    for pi in inst.captured.imports:
        for sa, ma in pi.attrs:
            mod_globals[ma] = proxy_import(pi.spec + (('.' + sa) if sa is not None else ''), pkg)
