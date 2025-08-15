"""
TODO:
 - auto_proxy_init can capture `import as` by scanning globals for sentinels
  - replaces _AutoProxyInitCapture._attrs dict outright
  - should raise on unbound or shadowed import - was probably imported for side-effects but will never get
    proxy imported
"""
import builtins
import contextlib
import functools
import importlib.util
import types
import typing as ta

from ..lazyglobals import LazyGlobals


##


class NamePackage(ta.NamedTuple):
    name: str
    package: str


class _ProxyInit:
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
            attrs: ta.Iterable[str | tuple[str, str]] | None = None,
    ) -> None:
        if isinstance(attrs, str):
            raise TypeError(attrs)

        if attrs is None:
            whole_attr = package.split('.')[-1]

            self._imps_by_attr[whole_attr] = self._Import(package, None)
            self._lazy_globals.set_fn(whole_attr, functools.partial(self.get, whole_attr))

        else:
            for attr in attrs:
                if isinstance(attr, tuple):
                    imp_attr, attr = attr
                else:
                    imp_attr = attr

                self._imps_by_attr[attr] = self._Import(package, imp_attr)
                self._lazy_globals.set_fn(attr, functools.partial(self.get, attr))

    def get(self, attr: str) -> ta.Any:
        try:
            imp = self._imps_by_attr[attr]
        except KeyError:
            raise AttributeError(attr)  # noqa

        val: ta.Any

        if imp.attr is None:
            val = importlib.import_module(imp.pkg, package=self._name_package.package)

        else:
            try:
                mod = self._mods_by_pkgs[imp.pkg]
            except KeyError:
                mod = importlib.import_module(imp.pkg, package=self._name_package.package)

            val = getattr(mod, imp.attr)

        return val


def proxy_init(
        init_globals: ta.MutableMapping[str, ta.Any],
        package: str,
        attrs: ta.Iterable[str | tuple[str, str]] | None = None,
) -> None:
    if isinstance(attrs, str):
        raise TypeError(attrs)

    init_name_package = NamePackage(
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

    pi.add(package, attrs)


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

            self.module = types.ModuleType(f'<{self.__class__.__qualname__}: {spec!r}>')

            self.attrs: dict[str, _AutoProxyInitCapture._ModuleAttr] = {}
            self.imported_whole = False

        def __repr__(self) -> str:
            return f'{self.__class__.__name__}({self.spec!r})'

    def __init__(self) -> None:
        super().__init__()

        self._modules: dict[_AutoProxyInitCapture.ModuleSpec, _AutoProxyInitCapture._Module] = {}
        self._attrs: dict[str, _AutoProxyInitCapture._ModuleAttr | _AutoProxyInitCapture._Module] = {}

    def _handle_import(
            self,
            module: _Module,
            *,
            from_list: ta.Sequence[str] | None,
    ) -> None:
        if from_list is None:
            if module.spec.level or not module.spec.name:
                raise AutoProxyInitError

            attr = module.spec.name

            try:
                xma: ta.Any = self._attrs[attr]
            except KeyError:
                pass

            else:
                if (
                        xma is not self._attrs.get(attr) or
                        not module.imported_whole
                ):
                    raise AutoProxyInitErrors.AttrError(str(module.spec), attr)

                return

            self._attrs[attr] = module
            module.imported_whole = True

        else:
            for attr in from_list:
                if attr == '*':
                    raise AutoProxyInitErrors.ImportStarForbiddenError(str(module.spec), from_list)

                try:
                    xma = getattr(module.module, attr)
                except AttributeError:
                    pass

                else:
                    if (
                            xma is not module.attrs.get(attr) or
                            xma is not self._attrs.get(attr)
                    ):
                        raise AutoProxyInitErrors.AttrError(str(module.spec), attr)

                    continue

                if attr in self._attrs:
                    raise AutoProxyInitErrors.AttrError(str(module.spec), attr)

                ma = _AutoProxyInitCapture._ModuleAttr(module, attr)
                self._attrs[attr] = ma
                module.attrs[attr] = ma
                setattr(module.module, attr, ma)

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
            module = self._modules[spec]
        except KeyError:
            module = self._Module(spec)
            self._modules[spec] = module

        self._handle_import(
            module,
            from_list=from_list,
        )

        return module.module

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

    def verify_globals(
            self,
            init_globals: ta.MutableMapping[str, ta.Any],  # noqa
    ) -> None:
        for attr, obj in self._attrs.items():
            try:
                xo = init_globals[attr]
            except KeyError:
                raise AutoProxyInitErrors.AttrError(None, attr) from None

            if isinstance(obj, _AutoProxyInitCapture._ModuleAttr):
                if xo is not obj:
                    raise AutoProxyInitErrors.AttrError(None, attr) from None

            elif isinstance(obj, _AutoProxyInitCapture._Module):
                if xo is not obj.module:
                    raise AutoProxyInitErrors.AttrError(None, attr) from None

            else:
                raise TypeError(obj)

    @property
    def all_attrs(self) -> ta.AbstractSet[str]:
        return self._attrs.keys()

    class ProxyInit(ta.NamedTuple):
        package: str
        attrs: ta.Sequence[str] | None

    def build_proxy_inits(self) -> list[ProxyInit]:
        lst: list[_AutoProxyInitCapture.ProxyInit] = []

        for module in self._modules.values():
            if module.imported_whole:
                lst.append(_AutoProxyInitCapture.ProxyInit(str(module.spec), None))

            if module.attrs:
                if not module.spec.name:
                    for attr in module.attrs:
                        if not module.spec.level:
                            raise AutoProxyInitError

                        lst.append(_AutoProxyInitCapture.ProxyInit('.' * module.spec.level + attr, None))

                else:
                    lst.append(_AutoProxyInitCapture.ProxyInit(str(module.spec), list(module.attrs)))

        return lst


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

    cap.verify_globals(init_globals)

    pis = cap.build_proxy_inits()

    for attr in cap.all_attrs:
        del init_globals[attr]

    for pi in pis:
        proxy_init(
            init_globals,
            pi.package,
            pi.attrs,
        )

    if eager:
        lg = LazyGlobals.install(init_globals)
        for attr in cap.all_attrs:
            lg.get(attr)
