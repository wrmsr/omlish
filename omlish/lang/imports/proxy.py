"""
TODO:
 - if already imported just return?
"""
import contextlib
import functools
import importlib.util
import types
import typing as ta

from ..lazyglobals import LazyGlobals
from .capture import ImportCapture
from .capture import _new_import_capture_hook


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


#


def auto_proxy_import(
        mod_globals: ta.MutableMapping[str, ta.Any],
        *,
        disable: bool = False,

        unreferenced_callback: ta.Callable[[ta.Mapping[str, ta.Sequence[str | None]]], None] | None = None,
        raise_unreferenced: bool = False,

        _stack_offset: int = 0,
) -> ta.ContextManager[ImportCapture]:
    inst = ImportCapture(
        mod_globals,
        _hook=_new_import_capture_hook(
            mod_globals,
            stack_offset=_stack_offset + 1,
        ),
        disable=disable,
    )

    @contextlib.contextmanager
    def inner() -> ta.Iterator[ImportCapture]:
        with inst.capture(
                unreferenced_callback=unreferenced_callback,
                raise_unreferenced=raise_unreferenced,
        ):
            yield inst

        pkg = mod_globals.get('__package__')
        for pi in inst.captured.imports:
            for sa, ma in pi.attrs:
                mod_globals[ma] = proxy_import(pi.spec + (('.' + sa) if sa is not None else ''), pkg)

    return inner()


##


class _ProxyInit:
    class NamePackage(ta.NamedTuple):
        name: str
        package: str

    class _Import(ta.NamedTuple):
        spec: str
        attr: str | None

    def __init__(
            self,
            lazy_globals: LazyGlobals,
            name_package: NamePackage,
    ) -> None:
        super().__init__()

        self._lazy_globals = lazy_globals
        self._name_package = name_package

        self._imps_by_attr: dict[str, _ProxyInit._Import] = {}
        self._mods_by_spec: dict[str, ta.Any] = {}

    @property
    def name_package(self) -> NamePackage:
        return self._name_package

    def add(
            self,
            package: str,
            attrs: ta.Iterable[tuple[str | None, str]],
    ) -> None:
        for imp_attr, as_attr in attrs:
            if imp_attr is None:
                self._imps_by_attr[as_attr] = self._Import(package, None)
                self._lazy_globals.set_fn(as_attr, functools.partial(self.get, as_attr))

            else:
                self._imps_by_attr[as_attr] = self._Import(package, imp_attr)
                self._lazy_globals.set_fn(as_attr, functools.partial(self.get, as_attr))

    def _import_module(self, name: str) -> ta.Any:
        return importlib.import_module(name, package=self._name_package.package)

    def get(self, attr: str) -> ta.Any:
        try:
            imp = self._imps_by_attr[attr]
        except KeyError:
            raise AttributeError(attr)  # noqa

        val: ta.Any

        if imp.attr is None:
            val = self._import_module(imp.spec)

        else:
            try:
                mod = self._mods_by_spec[imp.spec]
            except KeyError:
                mod = self._import_module(imp.spec)
                self._mods_by_spec[imp.spec] = mod

            val = getattr(mod, imp.attr)

        return val


def proxy_init(
        init_globals: ta.MutableMapping[str, ta.Any],
        spec: str,
        attrs: ta.Iterable[str | tuple[str | None, str | None] | None] | None = None,
) -> None:
    if isinstance(attrs, str):
        raise TypeError(attrs)

    if attrs is None:
        attrs = [None]

    whole_attr = spec.split('.')[-1]
    al: list[tuple[str | None, str]] = []
    for attr in attrs:
        if attr is None:
            al.append((None, whole_attr))

        elif isinstance(attr, str):
            al.append((attr, attr))

        elif isinstance(attr, tuple):
            imp_attr, as_attr = attr
            if as_attr is None:
                if imp_attr is None:
                    as_attr = whole_attr
                else:
                    as_attr = imp_attr
            al.append((imp_attr, as_attr))

        else:
            raise TypeError(attr)

    #

    init_name_package = _ProxyInit.NamePackage(
        init_globals['__name__'],
        init_globals['__package__'],
    )

    pi: _ProxyInit
    try:
        pi = init_globals['__proxy_init__']

    except KeyError:
        pi = _ProxyInit(
            LazyGlobals.install(init_globals),
            init_name_package,
        )
        init_globals['__proxy_init__'] = pi

    else:
        if pi.name_package != init_name_package:
            raise Exception(f'Wrong init name: {pi.name_package=} != {init_name_package=}')

    pi.add(spec, al)


#


def auto_proxy_init(
        init_globals: ta.MutableMapping[str, ta.Any],
        *,
        disable: bool = False,
        eager: bool = False,

        unreferenced_callback: ta.Callable[[ta.Mapping[str, ta.Sequence[str | None]]], None] | None = None,
        raise_unreferenced: bool = False,

        update_exports: bool = False,

        _stack_offset: int = 0,
) -> ta.ContextManager[ImportCapture]:
    inst = ImportCapture(
        init_globals,
        _hook=_new_import_capture_hook(
            init_globals,
            stack_offset=_stack_offset + 1,
        ),
        disable=disable,
    )

    @contextlib.contextmanager
    def inner() -> ta.Iterator[ImportCapture]:
        with inst.capture(
                unreferenced_callback=unreferenced_callback,
                raise_unreferenced=raise_unreferenced,
        ):
            yield inst

        for pi in inst.captured.imports:
            proxy_init(
                init_globals,
                pi.spec,
                pi.attrs,
            )

        if eager:
            lg = LazyGlobals.install(init_globals)

            for a in inst.captured.attrs:
                lg.get(a)

        if update_exports:
            inst.update_exports()

    return inner()
