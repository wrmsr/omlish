import contextlib
import importlib
import typing as ta

from .capture import ImportCapture


##


class NOT_SET:  # noqa
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError


@ta.final
class _SelfPatchingProxyImport:
    def __init__(
            self,
            mod_globals: ta.MutableMapping[str, ta.Any],
            mod_attr: str,
            spec: str,
            spec_attr: str | None,
    ) -> None:
        self.__dict__.update(
            __self_patching_proxy_import__mod_globals__=mod_globals,
            __self_patching_proxy_import__mod_attr__=mod_attr,
            __self_patching_proxy_import__spec__=spec,
            __self_patching_proxy_import__spec_attr__=spec_attr,
        )

    __self_patching_proxy_import__obj__: ta.Any = NOT_SET

    def __self_patching_proxy_import__get_obj__(self) -> ta.Any:
        if (obj := self.__self_patching_proxy_import__obj__) is NOT_SET:
            mod = importlib.import_module(
                self.__self_patching_proxy_import__spec__,
                package=self.__self_patching_proxy_import__mod_globals__.get('__package__'),
            )

            if (ma := self.__self_patching_proxy_import__mod_attr__) is not None:
                obj = getattr(mod, ma)
            else:
                obj = mod

            self.__self_patching_proxy_import__mod_globals__[self.__self_patching_proxy_import__mod_attr__] = obj

        return obj

    def __getattr__(self, attr: str) -> ta.Any:
        return getattr(self.__self_patching_proxy_import__get_obj__(), attr)

    def __setattr__(self, attr: str, value: ta.Any) -> None:
        setattr(self.__self_patching_proxy_import__get_obj__(), attr, value)

    def __delattr__(self, attr: str) -> None:
        delattr(self.__self_patching_proxy_import__get_obj__(), attr)


@contextlib.contextmanager
def auto_patch_proxy_import(
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

    for pi in inst.captured.imports:
        for sa, ma in pi.attrs:
            mod_globals[ma] = _SelfPatchingProxyImport(mod_globals, ma, pi.spec, sa)
