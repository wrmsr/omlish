"""
TODO:
 - _ProxyImports
 - if already imported just return?
  - no, need sub-imports..
 - seal on first use? or just per module? can't seal roots and still be usable
  - only if not hasattr?

See:
 - https://peps.python.org/pep-0810/
 - https://scientific-python.org/specs/spec-0001/
 - https://github.com/scientific-python/lazy-loader
"""
import contextlib
import functools
import importlib.util
import threading
import types
import typing as ta

from ..lazyglobals import LazyGlobals
from .capture import ImportCapture
from .capture import _new_import_capture_hook


##


class _ProxyImporter:
    def __init__(
            self,
            *,
            owner_globals: ta.MutableMapping[str, ta.Any] | None = None,
    ) -> None:
        super().__init__()

        self._owner_globals = owner_globals

        self._owner_name: str | None = owner_globals.get('__name__') if owner_globals else None

        # NOTE: Import machinery may be reentrant for things like gc ops and signal handling:
        # TODO: audit for reentrancy this lol
        # https://github.com/python/cpython/blob/72f25a8d9a5673d39c107cf522465a566b979ed5/Lib/importlib/_bootstrap.py#L233-L237  # noqa
        self._lock = threading.RLock()

        self._modules_by_name: dict[str, _ProxyImporter._Module] = {}
        self._modules_by_proxy_obj: dict[types.ModuleType, _ProxyImporter._Module] = {}

    class _Module:
        def __init__(
                self,
                name: str,
                getattr_handler: ta.Callable[['_ProxyImporter._Module', str], ta.Any],
                *,
                parent: ta.Optional['_ProxyImporter._Module'] = None,
        ) -> None:
            super().__init__()

            self.name = name
            self.parent = parent

            self.base_name = name.rpartition('.')[2]
            self.root: _ProxyImporter._Module = parent.root if parent is not None else self  # noqa

            self.children: dict[str, _ProxyImporter._Module] = {}
            self.descendants: set[_ProxyImporter._Module] = set()

            self.proxy_obj = types.ModuleType(f'<{self.__class__.__qualname__}: {name}>')
            self.proxy_obj.__file__ = None
            self.proxy_obj.__getattr__ = functools.partial(getattr_handler, self)  # type: ignore[method-assign]  # noqa

            self.pending_children: set[str] = set()
            self.pending_attrs: set[str] = set()

        real_obj: types.ModuleType | None = None

    def _get_or_make_module_locked(self, name: str) -> _Module:
        try:
            return self._modules_by_name[name]
        except KeyError:
            pass

        parent: _ProxyImporter._Module | None = None
        if '.' in name:
            rest, _, attr = name.rpartition('.')
            parent = self._get_or_make_module_locked(rest)

            if (
                    attr in parent.children or
                    attr in parent.pending_attrs or
                    ((ro := parent.real_obj) is not None and attr not in ro.__dict__)
            ):
                raise NotImplementedError

        module = self._modules_by_name[name] = _ProxyImporter._Module(
            name,
            self._handle_module_getattr,
        )

        self._modules_by_name[name] = module
        self._modules_by_proxy_obj[module.proxy_obj] = module

        if parent is not None:
            parent.pending_children.discard(module.base_name)
            parent.children[module.base_name] = module
            parent.root.descendants.add(module)

        return module

    def add_module(
            self,
            module: str,
            *,
            children: ta.Iterable[str] | None = None,
            attrs: ta.Iterable[str] | None = None,
    ) -> types.ModuleType:
        if isinstance(children, str):
            raise TypeError(children)

        with self._lock:
            if not children and not attrs and '.' in module:
                module, _, child = module.rpartition('.')
                children = [child]

            m = self._get_or_make_module_locked(module)

            for c in children or []:
                if m.real_obj is not None and c in m.real_obj.__dict__:
                    raise Exception(f'Already imported: {module}')

                m.pending_children.add(c)

            for a in attrs or []:
                if m.real_obj is not None and c in m.real_obj.__dict__:
                    raise Exception(f'Already imported: {module}')

                m.pending_attrs.add(a)

        return m.proxy_obj

    def _handle_module_getattr(self, module: _Module, attr: str) -> ta.Any:
        # FIXME: lock lol

        if attr in module.pending_children:
            if module.name == self._owner_name:
                val = importlib.import_module(f'{module.name}.{attr}')

            else:
                mod = __import__(
                    module.name,
                    self._owner_globals or {},
                    {},
                    [attr],
                    0,
                )

                # TODO: check if real_mod, or do something with real_mod ...
                val = getattr(mod, attr)

            return val

        if attr in module.pending_attrs:
            if (ro := module.real_obj) is None:
                ro = module.real_obj = importlib.import_module(module.name)

            return getattr(ro, attr)

        try:
            child = module.children[attr]
        except KeyError:
            pass
        else:
            return child.proxy_obj

        raise NotImplementedError

    def retrieve(self, spec: str) -> ta.Any:
        if '.' not in spec:
            return self._modules_by_name[spec].proxy_obj

        try:
            module = self._modules_by_name[spec]
        except KeyError:
            pass
        else:
            return module.proxy_obj

        rest, _, attr = spec.rpartition('.')
        module = self._modules_by_name[rest]
        return getattr(module.proxy_obj, attr)


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

            for a in ci.as_ or []:
                dct.setdefault(p.name, []).append(
                    (ci.module.base_name, a),
                )

        elif ci.module.kind == 'terminal':
            if ci.module.children:
                raise NotImplementedError

            for a in ci.as_ or []:
                dct.setdefault(ci.module.name, []).append(
                    (None, a),
                )

            for sa, da in ci.attrs or []:
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

        pi: _ProxyImporter
        try:
            pi = init_globals['__proxy_importer__']

        except KeyError:
            pi = _ProxyImporter(
                owner_globals=init_globals,
            )
            init_globals['__proxy_init__'] = pi

        else:
            if pi._owner_globals is not init_globals:  # noqa
                raise Exception

        lg = LazyGlobals.install(init_globals)

        for cm in inst.captured.modules.values():
            pi.add_module(
                cm.name,
                children=cm.children,
                attrs=cm.attrs,
            )

        for ci in inst.captured.imports.values():
            for a in ci.as_ or []:
                lg.set_fn(a, functools.partial(pi.retrieve, ci.module.name))
            for sa, da in ci.attrs or []:
                lg.set_fn(da, functools.partial(pi.retrieve, f'{ci.module.name}.{sa}'))

        if eager:
            for a in inst.captured.attrs:
                lg.get(a)

        if update_exports:
            inst.update_exports()

    return inner()
