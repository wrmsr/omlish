"""
TODO:
 - should raise on unbound or shadowed import - was probably imported for side-effects but will never get proxy imported
 - __getattr__ hook in fake modules, returning jit attrs
"""
import builtins
import contextlib
import functools
import importlib.util
import types
import typing as ta

from ..lazyglobals import LazyGlobals


##


class _ProxyInit:
    class NamePackage(ta.NamedTuple):
        name: str
        package: str

    class _Import(ta.NamedTuple):
        pkg: str
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
        self._mods_by_pkgs: dict[str, ta.Any] = {}

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
            val = self._import_module(imp.pkg)

        else:
            try:
                mod = self._mods_by_pkgs[imp.pkg]
            except KeyError:
                mod = self._import_module(imp.pkg)
                self._mods_by_pkgs[imp.pkg] = mod

            val = getattr(mod, imp.attr)

        return val


def proxy_init(
        init_globals: ta.MutableMapping[str, ta.Any],
        package: str,
        attrs: ta.Iterable[str | tuple[str | None, str | None] | None] | None = None,
) -> None:
    if isinstance(attrs, str):
        raise TypeError(attrs)

    if attrs is None:
        attrs = [None]

    whole_attr = package.split('.')[-1]
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

    pi.add(package, al)


##


class AutoProxyInitError(Exception):
    pass


class AutoProxyInitErrors:
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    class HookError(AutoProxyInitError):
        pass

    class AttrError(AutoProxyInitError):
        def __init__(self, module: str | None, name: str) -> None:
            super().__init__()

            self.module = module
            self.name = name

        def __repr__(self) -> str:
            return f'{self.__class__.__qualname__}(module={self.module!r}, name={self.name!r})'

    class ImportError(AutoProxyInitError):  # noqa
        def __init__(self, module: str, from_list: ta.Sequence[str] | None) -> None:
            super().__init__()

            self.module = module
            self.from_list = from_list

        def __repr__(self) -> str:
            return f'{self.__class__.__qualname__}(module={self.module!r}, from_list={self.from_list!r})'

    class ImportStarForbiddenError(ImportError):
        pass

    class UnproxiedImportForbiddenError(ImportError):
        pass


class _AutoProxyInitCapture:
    class ModuleSpec(ta.NamedTuple):
        name: str
        level: int

        def __str__(self) -> str:
            return f'{"." * self.level}{self.name}'

        def __repr__(self) -> str:
            return repr(str(self))

    def __init__(self) -> None:
        super().__init__()

        self._modules_by_spec: dict[_AutoProxyInitCapture.ModuleSpec, _AutoProxyInitCapture._Module] = {}
        self._modules_by_module_obj: dict[types.ModuleType, _AutoProxyInitCapture._Module] = {}

        self._attrs: dict[_AutoProxyInitCapture._ModuleAttr, tuple[_AutoProxyInitCapture._Module, str]] = {}

    #

    class _ModuleAttr:
        def __init__(self, module: '_AutoProxyInitCapture._Module', name: str) -> None:
            super().__init__()

            self.__module = module
            self.__name = name

        def __repr__(self) -> str:
            return f'<{self.__class__.__name__}: {f"{self.__module.spec}:{self.__name}"!r}>'

    class _Module:
        def __init__(self, spec: '_AutoProxyInitCapture.ModuleSpec') -> None:
            super().__init__()

            self.spec = spec

            self.module_obj = types.ModuleType(f'<{self.__class__.__qualname__}: {spec!r}>')
            self.initial_module_dict = dict(self.module_obj.__dict__)

            self.attrs: dict[str, _AutoProxyInitCapture._ModuleAttr] = {}
            self.imported_whole = False

        def __repr__(self) -> str:
            return f'{self.__class__.__name__}({self.spec!r})'

    def _handle_import(
            self,
            module: _Module,
            *,
            from_list: ta.Sequence[str] | None,
    ) -> None:
        if from_list is None:
            if module.spec.level or not module.spec.name:
                raise AutoProxyInitError

            module.imported_whole = True

        else:
            for attr in from_list:
                if attr == '*':
                    raise AutoProxyInitErrors.ImportStarForbiddenError(str(module.spec), from_list)

                try:
                    xma = getattr(module.module_obj, attr)
                except AttributeError:
                    pass

                else:
                    if (
                            xma is not module.attrs.get(attr) or
                            self._attrs[xma] != (module, attr)
                    ):
                        raise AutoProxyInitErrors.AttrError(str(module.spec), attr)

                    continue

                ma = _AutoProxyInitCapture._ModuleAttr(module, attr)
                module.attrs[attr] = ma
                self._attrs[ma] = (module, attr)
                setattr(module.module_obj, attr, ma)

    #

    _MOD_SELF_ATTR: ta.ClassVar[str] = '__auto_proxy_init_capture__'

    def _intercept_import(
            self,
            name: str,
            *,
            globals: ta.Mapping[str, ta.Any] | None = None,  # noqa
            from_list: ta.Sequence[str] | None = None,
            level: int = 0,
    ) -> types.ModuleType | None:
        if not (
                globals is not None and
                globals.get(self._MOD_SELF_ATTR) is self
        ):
            return None

        spec = _AutoProxyInitCapture.ModuleSpec(name, level)
        try:
            module = self._modules_by_spec[spec]
        except KeyError:
            module = self._Module(spec)
            self._modules_by_spec[spec] = module
            self._modules_by_module_obj[module.module_obj] = module

        self._handle_import(
            module,
            from_list=from_list,
        )

        return module.module_obj

    @contextlib.contextmanager
    def hook_context(
            self,
            init_globals: ta.MutableMapping[str, ta.Any],  # noqa
            *,
            forbid_unproxied_imports: bool = False,
    ) -> ta.Iterator[None]:
        if self._MOD_SELF_ATTR in init_globals:
            raise AutoProxyInitErrors.HookError

        old_import = builtins.__import__

        def new_import(
                name,
                globals=None,  # noqa
                locals=None,  # noqa
                fromlist=None,
                level=0,
        ):
            if (im := self._intercept_import(
                    name,
                    globals=globals,
                    from_list=fromlist,
                    level=level,
            )) is not None:
                return im

            if forbid_unproxied_imports:
                raise AutoProxyInitErrors.UnproxiedImportForbiddenError(
                    str(_AutoProxyInitCapture.ModuleSpec(name, level)),
                    fromlist,
                )

            return old_import(
                name,
                globals=globals,
                locals=locals,
                fromlist=fromlist,
                level=level,
            )

        #

        init_globals[self._MOD_SELF_ATTR] = self
        builtins.__import__ = new_import

        try:
            yield

        finally:
            if not (
                    init_globals[self._MOD_SELF_ATTR] is self and
                    builtins.__import__ is new_import
            ):
                raise AutoProxyInitErrors.HookError

            del init_globals[self._MOD_SELF_ATTR]
            builtins.__import__ = old_import

    #

    def verify_state(
            self,
            init_globals: ta.MutableMapping[str, ta.Any],  # noqa
    ) -> None:
        for m in self._modules_by_spec.values():
            for a, o in m.module_obj.__dict__.items():
                try:
                    i = m.initial_module_dict[a]

                except KeyError:
                    if o is not m.attrs[a]:
                        raise AutoProxyInitErrors.AttrError(str(m.spec), a) from None

                else:
                    if o != i:
                        raise AutoProxyInitErrors.AttrError(str(m.spec), a)

    #

    class ProxyInit(ta.NamedTuple):
        package: str
        attrs: ta.Sequence[tuple[str | None, str]]

    class BuiltProxyInits(ta.NamedTuple):
        proxy_inits: ta.Sequence['_AutoProxyInitCapture.ProxyInit']

    def build_proxy_inits(
            self,
            init_globals: ta.MutableMapping[str, ta.Any],  # noqa
    ) -> BuiltProxyInits:
        dct: dict[_AutoProxyInitCapture._Module, list[tuple[str | None, str]]] = {}

        rem_whole_mods: set[_AutoProxyInitCapture._Module] = {m for m in self._modules_by_spec.values() if m.imported_whole}  # noqa
        rem_mod_attrs: set[_AutoProxyInitCapture._ModuleAttr] = set(self._attrs)

        for attr, obj in init_globals.items():
            if isinstance(obj, _AutoProxyInitCapture._ModuleAttr):
                try:
                    m, a = self._attrs[obj]
                except KeyError:
                    raise AutoProxyInitErrors.AttrError(None, attr) from None
                dct.setdefault(m, []).append((a, attr))
                rem_mod_attrs.discard(obj)

            elif isinstance(obj, _AutoProxyInitCapture._Module):
                raise AutoProxyInitErrors.AttrError(None, attr) from None

            elif isinstance(obj, types.ModuleType):
                try:
                    m = self._modules_by_module_obj[obj]
                except KeyError:
                    continue
                if not m.imported_whole:
                    raise RuntimeError(f'AutoProxyInit module {m.spec!r} not imported_whole')
                dct.setdefault(m, []).append((None, attr))
                rem_whole_mods.discard(m)

        lst: list[_AutoProxyInitCapture.ProxyInit] = []
        for m, ts in dct.items():
            if not m.spec.name:
                if not m.spec.level:
                    raise AutoProxyInitError
                for imp_attr, as_attr in ts:
                    if not imp_attr:
                        raise RuntimeError
                    lst.append(_AutoProxyInitCapture.ProxyInit(
                        '.' * m.spec.level + imp_attr,
                        [(None, as_attr)],
                    ))

            else:
                lst.append(_AutoProxyInitCapture.ProxyInit(
                    str(m.spec),
                    ts,
                ))

        return _AutoProxyInitCapture.BuiltProxyInits(
            lst,
        )


@contextlib.contextmanager
def auto_proxy_init(
        init_globals: ta.MutableMapping[str, ta.Any],
        *,
        disable: bool = False,
        eager: bool = False,
) -> ta.Iterator[None]:
    """
    This is a bit extreme - use sparingly. It relies on an interpreter-global import lock, but much of the ecosystem
    implicitly does anyway. It further relies on temporarily patching `__builtins__.__import__`, but could be switched
    to use any number of other import hooks.
    """

    if disable:
        yield
        return

    cap = _AutoProxyInitCapture()

    with cap.hook_context(init_globals):
        yield

    cap.verify_state(init_globals)

    blt = cap.build_proxy_inits(init_globals)

    for pi in blt.proxy_inits:
        for _, a in pi.attrs:
            del init_globals[a]

        proxy_init(
            init_globals,
            pi.package,
            pi.attrs,
        )

    if eager:
        lg = LazyGlobals.install(init_globals)

        for pi in blt.proxy_inits:
            for _, a in pi.attrs:
                lg.get(a)
