import contextlib
import functools
import importlib.util
import types
import typing as ta

from ..lazyglobals import LazyGlobals
from .capture import ImportCapture
from .capture import _new_import_capture_hook


##


def _translate_old_style_import_capture(
        cap: ImportCapture.Captured,
) -> ta.Mapping[str, ta.Sequence[tuple[str | None, str]]]:
    dct: dict[str, list[tuple[str | None, str]]] = {}

    for ci in cap.imports.values():
        if ci.module.kind == 'leaf':
            if (p := ci.module.parent) is None:
                raise NotImplementedError

            if ci.attrs:
                raise NotImplementedError

            for a in ci.as_:
                dct.setdefault(p.name, []).append(
                    (ci.module.base_name, a),
                )

        elif ci.module.kind == 'terminal':
            if ci.module.children:
                raise NotImplementedError

            for a in ci.as_:
                dct.setdefault(ci.module.name, []).append(
                    (None, a),
                )

            for sa, da in ci.attrs:
                dct.setdefault(ci.module.name, []).append(
                    (sa, da),
                )

        else:
            raise NotImplementedError

    return dct


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

        unreferenced_callback: ta.Callable[[ta.Sequence[str]], None] | None = None,
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

        for spec, attrs in _translate_old_style_import_capture(inst.captured).items():
            for sa, ma in attrs:
                mod_globals[ma] = proxy_import(spec + (('.' + sa) if sa is not None else ''))

    return inner()


##


class _ProxyInit:
    class NamePackage(ta.NamedTuple):
        name: str
        package: str

    class _Import(ta.NamedTuple):
        name: str
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

    @property
    def name_package(self) -> NamePackage:
        return self._name_package

    def add(
            self,
            name: str,
            attrs: ta.Iterable[tuple[str | None, str]],
    ) -> None:
        for imp_attr, as_attr in attrs:
            if imp_attr is None:
                self._imps_by_attr[as_attr] = self._Import(name, None)
                self._lazy_globals.set_fn(as_attr, functools.partial(self.get, as_attr))

            else:
                self._imps_by_attr[as_attr] = self._Import(name, imp_attr)
                self._lazy_globals.set_fn(as_attr, functools.partial(self.get, as_attr))

    def get(self, attr: str) -> ta.Any:
        try:
            imp = self._imps_by_attr[attr]
        except KeyError:
            raise AttributeError(attr)  # noqa

        val: ta.Any

        if imp.attr is None:
            val = importlib.import_module(imp.name)

        elif imp.name == self._name_package.name:
            val = importlib.import_module(f'{imp.name}.{imp.attr}')

        else:
            mod = __import__(
                imp.name,
                self._lazy_globals._globals,  # noqa
                {},
                [imp.attr],
                0,
            )

            val = getattr(mod, imp.attr)

        return val


def proxy_init(
        init_globals: ta.MutableMapping[str, ta.Any],
        spec: str,
        attrs: ta.Iterable[str | tuple[str | None, str | None] | None] | None = None,
) -> None:
    name = importlib.util.resolve_name(
        spec,
        package=init_globals['__package__'] if spec.startswith('.') else None,
    )

    #

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

    pi.add(name, al)


#


def auto_proxy_init(
        init_globals: ta.MutableMapping[str, ta.Any],
        *,
        disable: bool = False,
        eager: bool = False,

        unreferenced_callback: ta.Callable[[ta.Sequence[str]], None] | None = None,
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

        for spec, attrs in _translate_old_style_import_capture(inst.captured).items():
            proxy_init(
                init_globals,
                spec,
                attrs,
            )

        if eager:
            lg = LazyGlobals.install(init_globals)

            for a in inst.captured.attrs:
                lg.get(a)

        if update_exports:
            inst.update_exports()

    return inner()
