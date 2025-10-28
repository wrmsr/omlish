"""
TODO:
 - if already imported just return?
  - no, need sub-imports..
 - seal on first use? or just per module? can't seal roots and still be usable
  - only if not hasattr?
 - audit for deadlock risk - does importlib._bootstrap do it for us? do we need a global _ProxyImporter lock? would only
   happen on reification
 - ProxyImportError
 - detect import reification in own module body - user is failing to properly 'hands-off' lazy import
  - bonus points detect when done specifically for a type annotation

See:
 - https://peps.python.org/pep-0810/
  - https://github.com/LazyImportsCabal/cpython/tree/lazy
  - https://developers.facebook.com/blog/post/2022/06/15/python-lazy-imports-with-cinder/
  - https://engineering.fb.com/2024/01/18/developer-tools/lazy-imports-cinder-machine-learning-meta/
  - https://www.hudsonrivertrading.com/hrtbeat/inside-hrts-python-fork/
  - https://bugreports.qt.io/browse/PYSIDE-2404
 - https://scientific-python.org/specs/spec-0001/
 - https://github.com/scientific-python/lazy-loader
"""
import functools
import importlib.util
import threading
import types
import typing as ta

from ..lazyglobals import LazyGlobals
from .capture import ImportCapture
from .capture import _new_import_capture_hook


_ProxyImporterModuleAttr: ta.TypeAlias = ta.Literal[
    'child',  # 'outranks' proxy_attr - all child attrs must be proxy_attrs but not vice versa
    'proxy_attr',
    'pending_child',
    'pending_attr',
]


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
            self.proxy_obj.__getattr__ = functools.partial(getattr_handler, self)  # type: ignore[method-assign]

            self.pending_children: set[str] = set()
            self.pending_attrs: set[str] = set()

        real_obj: types.ModuleType | None = None

        def __repr__(self) -> str:
            return f'{self.__class__.__name__}<{self.name}{"!" if self.real_obj is not None else ""}>'

        def find_attr(self, attr: str) -> _ProxyImporterModuleAttr | None:
            is_child = attr in self.children
            is_proxy_attr = attr in self.proxy_obj.__dict__
            is_pending_child = attr in self.pending_children
            is_pending_attr = attr in self.pending_attrs

            if is_child:
                if (
                        not is_proxy_attr or
                        is_pending_child or
                        is_pending_attr
                ):
                    raise RuntimeError
                return 'child'

            elif is_proxy_attr:
                if (
                        is_pending_child or
                        is_pending_attr
                ):
                    raise RuntimeError
                return 'proxy_attr'

            elif is_pending_child:
                if (
                        is_child or
                        is_proxy_attr or
                        is_pending_attr
                ):
                    raise RuntimeError
                return 'pending_child'

            elif is_pending_attr:
                if (
                        is_child or
                        is_proxy_attr or
                        is_pending_child
                ):
                    raise RuntimeError
                return 'pending_attr'

            else:
                return None

    #

    def _get_or_make_module_locked(self, name: str) -> _Module:
        try:
            return self._modules_by_name[name]
        except KeyError:
            pass

        parent: _ProxyImporter._Module | None = None
        if '.' in name:
            rest, _, attr = name.rpartition('.')
            parent = self._get_or_make_module_locked(rest)

            fa = parent.find_attr(attr)
            if not (fa == 'pending_child' or fa is None):
                raise RuntimeError

            if (ro := parent.real_obj) is not None and attr not in ro.__dict__:
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
            setattr(parent.proxy_obj, module.base_name, module.proxy_obj)
            parent.root.descendants.add(module)

        return module

    def _extend_module_locked(
            self,
            module: _Module,
            *,
            children: ta.Iterable[str] | None = None,
            attrs: ta.Iterable[str] | None = None,
    ) -> None:
        for l in (children, attrs):
            for n in l or ():
                if n in module.proxy_obj.__dict__:
                    raise NotImplementedError

                if (ro := module.real_obj) is not None and n in ro.__dict__:
                    raise NotImplementedError

        for n in children or ():
            fa = module.find_attr(n)
            if not (fa == 'pending_child' or fa is None):
                raise RuntimeError

        for n in attrs or ():
            fa = module.find_attr(n)
            if not (fa == 'pending_attr' or fa is None):
                raise RuntimeError

        #

        if children:
            module.pending_children.update(n for n in children if n not in module.children)
        if attrs:
            module.pending_attrs.update(attrs)

    def _retrieve_from_module_locked(self, module: _Module, attr: str) -> ta.Any:
        fa = module.find_attr(attr)

        if fa == 'child' or fa == 'proxy_attr':
            return module.proxy_obj.__dict__[attr]

        val: ta.Any

        if fa == 'pending_child':
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

                val = getattr(mod, attr)

            module.pending_children.remove(attr)

        elif fa == 'pending_attr' or fa is None:
            if module.name == self._owner_name:
                raise NotImplementedError

            if (ro := module.real_obj) is None:
                ro = module.real_obj = importlib.import_module(module.name)

            val = getattr(ro, attr)

            if fa == 'pending_attr':
                module.pending_attrs.remove(attr)

        else:
            raise TypeError(fa)

        setattr(module.proxy_obj, attr, val)
        return val

    #

    def _handle_module_getattr(self, module: _Module, attr: str) -> ta.Any:
        with self._lock:
            return self._retrieve_from_module_locked(module, attr)

    def add(
            self,
            module: str,
            *,
            children: ta.Iterable[str] | None = None,
            attrs: ta.Iterable[str] | None = None,
    ) -> types.ModuleType:
        if isinstance(children, str):
            raise TypeError(children)

        # Leaf modules get collapsed into parents' pending_children
        if not children and not attrs and '.' in module:
            module, _, child = module.rpartition('.')
            children = [child]

        with self._lock:
            m = self._get_or_make_module_locked(module)

            if children or attrs:
                self._extend_module_locked(
                    m,
                    children=children,
                    attrs=attrs,
                )

        return m.proxy_obj

    def get_module(self, name: str) -> types.ModuleType:
        try:
            return self._modules_by_name[name].proxy_obj
        except KeyError:
            pass

        with self._lock:
            return self._get_or_make_module_locked(name).proxy_obj

    def lookup(self, spec: str) -> ta.Any:
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


#


_MODULE_PROXY_IMPORTER_GLOBAL_NAME = '__proxy_importer__'


def _get_module_proxy_importer(mod_globals: ta.MutableMapping[str, ta.Any]) -> _ProxyImporter:
    """Assumed to only be called in a module body - no locking is done."""

    pi: _ProxyImporter
    try:
        pi = mod_globals[_MODULE_PROXY_IMPORTER_GLOBAL_NAME]

    except KeyError:
        pi = _ProxyImporter(
            owner_globals=mod_globals,
        )
        mod_globals[_MODULE_PROXY_IMPORTER_GLOBAL_NAME] = pi

    else:
        if pi.__class__ is not _ProxyImporter:
            raise TypeError(pi)

        if pi._owner_globals is not mod_globals:  # noqa
            raise RuntimeError

    return pi


##


def proxy_import(
        spec: str,
        package: str | None = None,
        extras: ta.Iterable[str] | None = None,
        *,
        no_cache: bool = False,
) -> types.ModuleType:
    """'Legacy' proxy import mechanism."""

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

        v = getattr(omod, att)

        if not no_cache:
            setattr(lmod, att, v)

        return v

    lmod = types.ModuleType(spec)
    lmod.__getattr__ = __getattr__  # type: ignore[method-assign]
    return lmod


#


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

    pi = _get_module_proxy_importer(init_globals)
    lg = LazyGlobals.install(init_globals)

    pi.add(
        name,
        children=[r for l, r in al if r is not None],
    )

    for imp_attr, as_attr in al:
        lg.set_fn(as_attr, functools.partial(pi.lookup, name if imp_attr is None else f'{name}.{imp_attr}'))


##


class _AutoProxy:
    def __init__(
            self,
            mod_globals: ta.MutableMapping[str, ta.Any],
            *,
            disable: bool = False,
            eager: bool = False,

            unreferenced_callback: ta.Callable[[ta.Sequence[str]], None] | None = None,
            raise_unreferenced: bool = False,

            update_exports: bool = False,

            _stack_offset: int = 0,
            _capture_impl: str | None = None,
    ) -> None:
        super().__init__()

        self._mod_globals = mod_globals

        self._disabled = disable
        self._eager = eager

        self._unreferenced_callback = unreferenced_callback
        self._raise_unreferenced = raise_unreferenced

        self._update_exports = update_exports

        self._ic = ImportCapture(
            mod_globals,
            _hook=_new_import_capture_hook(
                mod_globals,
                stack_offset=_stack_offset + 1,
                capture_impl=_capture_impl,
            ),
            disable=disable,
        )
        self._icc: ta.Any = None

    def __enter__(self) -> ImportCapture:
        if self._icc is not None:
            raise RuntimeError

        self._icc = self._ic.capture(
            unreferenced_callback=self._unreferenced_callback,
            raise_unreferenced=self._raise_unreferenced,
        )

        return self._icc.__enter__()  # noqa

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._icc is None:
            raise RuntimeError

        self._icc.__exit__(exc_type, exc_val, exc_tb)

        if not self._disabled and exc_type is None:
            self._install()

    # @abc.abstractmethod
    def _install(self) -> None:
        raise NotImplementedError


@ta.final
class _AutoProxyImport(_AutoProxy):
    def _install(self) -> None:
        cap = self._ic.captured

        for cm in cap.modules.values():
            if cm.attrs:
                raise RuntimeError

        pi = _get_module_proxy_importer(self._mod_globals)

        for cm in cap.modules.values():
            pi.add(
                cm.name,
                children=cm.children,
            )

        for ci in cap.imports.values():
            pm = pi.get_module(ci.module.name)
            for a in ci.as_ or ():
                self._mod_globals[a] = pm

        if self._eager:
            for ci in cap.imports.values():
                pi.lookup(ci.module.name)

        if self._update_exports:
            self._ic.update_exports()


@ta.final
class _AutoProxyInit(_AutoProxy):
    def _install(self) -> None:
        cap = self._ic.captured

        pi = _get_module_proxy_importer(self._mod_globals)
        lg = LazyGlobals.install(self._mod_globals)

        for cm in cap.modules.values():
            pi.add(
                cm.name,
                children=cm.children,
                attrs=cm.attrs,
            )

        for ci in cap.imports.values():
            for a in ci.as_ or ():
                lg.set_fn(a, functools.partial(pi.lookup, ci.module.name))
            for sa, da in ci.attrs or ():
                lg.set_fn(da, functools.partial(pi.lookup, f'{ci.module.name}.{sa}'))

        if self._eager:
            for a in cap.attrs:
                lg.get(a)

        if self._update_exports:
            self._ic.update_exports()


auto_proxy_import = _AutoProxyImport
auto_proxy_init = _AutoProxyInit
