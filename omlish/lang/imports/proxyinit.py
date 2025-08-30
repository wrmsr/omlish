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

    class UnreferencedImportsError(AutoProxyInitError):
        def __init__(self, unreferenced: ta.Mapping[str, ta.Sequence[str | None]]) -> None:
            super().__init__()

            self.unreferenced = unreferenced

        def __repr__(self) -> str:
            return f'{self.__class__.__qualname__}(unreferenced={self.unreferenced!r})'

    class CaptureInProgressError(AutoProxyInitError):
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
        def __init__(
                self,
                module: '_AutoProxyInitCapture._Module',
                name: str,
        ) -> None:
            super().__init__()

            self.__module = module
            self.__name = name

        def __repr__(self) -> str:
            return f'<{self.__class__.__name__}: {f"{self.__module.spec}:{self.__name}"!r}>'

    class _Module:
        def __init__(
                self,
                spec: '_AutoProxyInitCapture.ModuleSpec',
                *,
                getattr_handler: ta.Callable[['_AutoProxyInitCapture._Module', str], ta.Any] | None = None,
        ) -> None:
            super().__init__()

            self.spec = spec

            self.module_obj = types.ModuleType(f'<{self.__class__.__qualname__}: {spec!r}>')
            if getattr_handler is not None:
                self.module_obj.__getattr__ = functools.partial(getattr_handler, self)  # type: ignore[method-assign]  # noqa
            self.initial_module_dict = dict(self.module_obj.__dict__)

            self.contents: dict[str, _AutoProxyInitCapture._ModuleAttr | types.ModuleType] = {}
            self.imported_whole = False

        def __repr__(self) -> str:
            return f'{self.__class__.__name__}({self.spec!r})'

    def _get_or_make_module(self, spec: ModuleSpec) -> _Module:
        try:
            return self._modules_by_spec[spec]
        except KeyError:
            pass

        module = self._Module(
            spec,
            getattr_handler=self._handle_module_getattr,
        )
        self._modules_by_spec[spec] = module
        self._modules_by_module_obj[module.module_obj] = module
        return module

    def _handle_module_getattr(self, module: _Module, attr: str) -> ta.Any:
        if attr in module.contents:
            raise AutoProxyInitErrors.AttrError(str(module.spec), attr)

        v: _AutoProxyInitCapture._ModuleAttr | types.ModuleType
        if not module.spec.name:
            if not module.spec.level:
                raise AutoProxyInitError
            cs = _AutoProxyInitCapture.ModuleSpec(attr, module.spec.level)
            cm = self._get_or_make_module(cs)
            cm.imported_whole = True
            v = cm.module_obj

        else:
            ma = _AutoProxyInitCapture._ModuleAttr(module, attr)
            self._attrs[ma] = (module, attr)
            v = ma

        module.contents[attr] = v
        setattr(module.module_obj, attr, v)
        return v

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

                x = getattr(module.module_obj, attr)

                bad = False
                if x is not module.contents.get(attr):
                    bad = True
                if isinstance(x, _AutoProxyInitCapture._ModuleAttr):
                    if self._attrs[x] != (module, attr):
                        bad = True
                elif isinstance(x, types.ModuleType):
                    if x not in self._modules_by_module_obj:
                        bad = True
                else:
                    bad = True
                if bad:
                    raise AutoProxyInitErrors.AttrError(str(module.spec), attr)

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
        module = self._get_or_make_module(spec)

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
                    if o is not m.contents[a]:
                        raise AutoProxyInitErrors.AttrError(str(m.spec), a) from None

                else:
                    if o != i:
                        raise AutoProxyInitErrors.AttrError(str(m.spec), a)

    #

    def build_proxy_inits(
            self,
            init_globals: ta.MutableMapping[str, ta.Any],  # noqa
            *,
            collect_unreferenced: bool = False,
    ) -> 'AutoProxyInit.CapturedProxyInits':
        dct: dict[_AutoProxyInitCapture._Module, list[tuple[str | None, str]]] = {}

        rem_whole_mods: set[_AutoProxyInitCapture._Module] = set()
        rem_mod_attrs: set[_AutoProxyInitCapture._ModuleAttr] = set()
        if collect_unreferenced:
            rem_whole_mods.update([m for m in self._modules_by_spec.values() if m.imported_whole])
            rem_mod_attrs.update(self._attrs)

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

        lst: list[AutoProxyInit.ProxyInit] = []
        for m, ts in dct.items():
            if not m.spec.name:
                if not m.spec.level:
                    raise AutoProxyInitError
                for imp_attr, as_attr in ts:
                    if not imp_attr:
                        raise RuntimeError
                    lst.append(AutoProxyInit.ProxyInit(
                        '.' * m.spec.level + imp_attr,
                        [(None, as_attr)],
                    ))

            else:
                lst.append(AutoProxyInit.ProxyInit(
                    str(m.spec),
                    ts,
                ))

        unreferenced: dict[str, list[str | None]] | None = None
        if collect_unreferenced and (rem_whole_mods or rem_mod_attrs):
            unreferenced = {}
            for m in rem_whole_mods:
                unreferenced.setdefault(str(m.spec), []).append(None)
            for ma in rem_mod_attrs:
                m, a = self._attrs[ma]
                unreferenced.setdefault(str(m.spec), []).append(a)

        return AutoProxyInit.CapturedProxyInits(
            lst,
            unreferenced,
        )


class AutoProxyInit:
    class ProxyInit(ta.NamedTuple):
        package: str
        attrs: ta.Sequence[tuple[str | None, str]]

    class CapturedProxyInits(ta.NamedTuple):
        proxy_inits: ta.Sequence['AutoProxyInit.ProxyInit']
        unreferenced: ta.Mapping[str, ta.Sequence[str | None]] | None

        @property
        def attrs(self) -> ta.Iterator[str]:
            for pi in self.proxy_inits:
                for _, a in pi.attrs:
                    yield a

    #

    def __init__(
            self,
            init_globals: ta.MutableMapping[str, ta.Any],
            *,
            disable: bool = False,
            eager: bool = False,
    ) -> None:
        super().__init__()

        self._init_globals = init_globals

        self._disable = disable
        self._eager = eager

    @property
    def disable(self) -> bool:
        return self._disable

    @property
    def eager(self) -> bool:
        return self._eager

    #

    class _Result(ta.NamedTuple):
        captured: 'AutoProxyInit.CapturedProxyInits'

    _result_: _Result | None = None

    @property
    def _result(self) -> _Result:
        if (rs := self._result_) is None:
            raise AutoProxyInitErrors.CaptureInProgressError
        return rs

    @property
    def is_complete(self) -> bool:
        return self._result_ is not None

    @property
    def captured(self) -> CapturedProxyInits:
        return self._result.captured

    #

    @contextlib.contextmanager
    def _capture(
            self,
            *,
            unreferenced_callback: ta.Callable[[ta.Mapping[str, ta.Sequence[str | None]]], None] | None = None,
            raise_unreferenced: bool = False,
    ) -> ta.Iterator[None]:
        if self._result_ is not None:
            raise AutoProxyInitError('capture already complete')

        if self._disable:
            self._result_ = AutoProxyInit._Result(
                AutoProxyInit.CapturedProxyInits(
                    [],
                    None,
                ),
            )
            yield
            return

        cap = _AutoProxyInitCapture()

        with cap.hook_context(self._init_globals):
            yield

        cap.verify_state(self._init_globals)

        blt = cap.build_proxy_inits(
            self._init_globals,
            collect_unreferenced=unreferenced_callback is not None or raise_unreferenced,
        )

        if blt.unreferenced:
            if unreferenced_callback:
                unreferenced_callback(blt.unreferenced)
            if raise_unreferenced:
                raise AutoProxyInitErrors.UnreferencedImportsError(blt.unreferenced)

        for pi in blt.proxy_inits:
            for _, a in pi.attrs:
                del self._init_globals[a]

            proxy_init(
                self._init_globals,
                pi.package,
                pi.attrs,
            )

        if self._eager:
            lg = LazyGlobals.install(self._init_globals)

            for a in blt.attrs:
                lg.get(a)

        self._result_ = AutoProxyInit._Result(
            blt,
        )

    #

    def update_exports(self) -> None:
        cap = self._result.captured

        try:
            al: ta.Any = self._init_globals['__all__']
        except KeyError:
            al = self._init_globals['__all__'] = [k for k in self._init_globals if not k.startswith('_')]
        else:
            if not isinstance(al, ta.MutableSequence):
                al = self._init_globals['__all__'] = list(al)

        al_s = set(al)
        for a in cap.attrs:
            if a not in al_s:
                al.append(a)
                al_s.add(a)


@contextlib.contextmanager
def auto_proxy_init(
        init_globals: ta.MutableMapping[str, ta.Any],
        *,
        disable: bool = False,
        eager: bool = False,

        unreferenced_callback: ta.Callable[[ta.Mapping[str, ta.Sequence[str | None]]], None] | None = None,
        raise_unreferenced: bool = False,

        update_exports: bool = False,
) -> ta.Iterator[AutoProxyInit]:
    """
    This is a bit extreme - use sparingly. It relies on an interpreter-global import lock, but much of the ecosystem
    implicitly does anyway. It further relies on temporarily patching `__builtins__.__import__`, but could be switched
    to use any number of other import hooks.
    """

    inst = AutoProxyInit(
        init_globals,
        disable=disable,
        eager=eager,
    )

    with inst._capture(  # noqa
        unreferenced_callback=unreferenced_callback,
        raise_unreferenced=raise_unreferenced,
    ):
        yield inst

    if update_exports:
        inst.update_exports()
