"""
TODO:
 - proxy_init 'as' alias support - attrs of (src, dst)
"""
import contextlib
import importlib.util
import sys
import types
import typing as ta


##


def can_import(name: str, package: str | None = None) -> bool:
    try:
        spec = importlib.util.find_spec(name, package)
    except ImportError:
        return False
    else:
        return spec is not None


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


def proxy_import(
        name: str,
        package: str | None = None,
        extras: ta.Iterable[str] | None = None,
) -> types.ModuleType:
    if isinstance(extras, str):
        raise TypeError(extras)

    omod = None

    def __getattr__(att):  # noqa
        nonlocal omod
        if omod is None:
            omod = importlib.import_module(name, package=package)
            if extras:
                for x in extras:
                    importlib.import_module(f'{name}.{x}', package=package)
        return getattr(omod, att)

    lmod = types.ModuleType(name)
    lmod.__getattr__ = __getattr__  # type: ignore
    return lmod


##


SPECIAL_IMPORTABLE: ta.AbstractSet[str] = frozenset([
    '__init__.py',
    '__main__.py',
])


def yield_importable(
        package_root: str,
        *,
        recursive: bool = False,
        filter: ta.Callable[[str], bool] | None = None,  # noqa
        include_special: bool = False,
) -> ta.Iterator[str]:
    from importlib import resources

    def rec(cur):
        if cur.split('.')[-1] == '__pycache__':
            return

        try:
            module = sys.modules[cur]
        except KeyError:
            try:
                __import__(cur)
            except ImportError:
                return
            module = sys.modules[cur]

        # FIXME: pyox
        if getattr(module, '__file__', None) is None:
            return

        for file in resources.files(cur).iterdir():
            if file.is_file() and file.name.endswith('.py'):
                if not (include_special or file.name not in SPECIAL_IMPORTABLE):
                    continue

                name = cur + '.' + file.name[:-3]
                if filter is not None and not filter(name):
                    continue

                yield name

            elif recursive and file.is_dir():
                name = cur + '.' + file.name
                if filter is not None and not filter(name):
                    continue
                with contextlib.suppress(ImportError, NotImplementedError):
                    yield from rec(name)

    yield from rec(package_root)


def yield_import_all(
        package_root: str,
        *,
        globals: dict[str, ta.Any] | None = None,  # noqa
        locals: dict[str, ta.Any] | None = None,  # noqa
        recursive: bool = False,
        filter: ta.Callable[[str], bool] | None = None,  # noqa
        include_special: bool = False,
) -> ta.Iterator[str]:
    for import_path in yield_importable(
            package_root,
            recursive=recursive,
            filter=filter,
            include_special=include_special,
    ):
        __import__(import_path, globals=globals, locals=locals)
        yield import_path


def import_all(
        package_root: str,
        *,
        recursive: bool = False,
        filter: ta.Callable[[str], bool] | None = None,  # noqa
        include_special: bool = False,
) -> None:
    for _ in yield_import_all(
            package_root,
            recursive=recursive,
            filter=filter,
            include_special=include_special,
    ):
        pass


def try_import(spec: str) -> types.ModuleType | None:
    s = spec.lstrip('.')
    l = len(spec) - len(s)
    try:
        return __import__(s, globals(), level=l)
    except ImportError:
        return None


##


def resolve_import_name(name: str, package: str | None = None) -> str:
    level = 0

    if name.startswith('.'):
        if not package:
            raise TypeError("the 'package' argument is required to perform a relative import for {name!r}")
        for character in name:
            if character != '.':
                break
            level += 1

    name = name[level:]

    if not isinstance(name, str):
        raise TypeError(f'module name must be str, not {type(name)}')
    if level < 0:
        raise ValueError('level must be >= 0')
    if level > 0:
        if not isinstance(package, str):
            raise TypeError('__package__ not set to a string')
        elif not package:
            raise ImportError('attempted relative import with no known parent package')
    if not name and level == 0:
        raise ValueError('Empty module name')

    if level > 0:
        bits = package.rsplit('.', level - 1)  # type: ignore
        if len(bits) < level:
            raise ImportError('attempted relative import beyond top-level package')
        base = bits[0]
        name = f'{base}.{name}' if name else base

    return name


##


_REGISTERED_CONDITIONAL_IMPORTS: dict[str, list[str] | None] = {}


def _register_conditional_import(when: str, then: str, package: str | None = None) -> None:
    wn = resolve_import_name(when, package)
    tn = resolve_import_name(then, package)
    if tn in sys.modules:
        return
    if wn in sys.modules:
        __import__(tn)
    else:
        tns = _REGISTERED_CONDITIONAL_IMPORTS.setdefault(wn, [])
        if tns is None:
            raise Exception(f'Conditional import trigger already cleared: {wn=} {tn=}')
        tns.append(tn)


def _trigger_conditional_imports(package: str) -> None:
    tns = _REGISTERED_CONDITIONAL_IMPORTS.get(package, [])
    if tns is None:
        raise Exception(f'Conditional import trigger already cleared: {package=}')
    _REGISTERED_CONDITIONAL_IMPORTS[package] = None
    for tn in tns:
        __import__(tn)


##


class NamePackage(ta.NamedTuple):
    name: str
    package: str


class _ProxyInit:
    class _Import(ta.NamedTuple):
        pkg: str
        attr: str

    def __init__(
            self,
            name_package: NamePackage,
            *,
            globals: ta.MutableMapping[str, ta.Any] | None = None,  # noqa
            update_globals: bool = False,
    ) -> None:
        super().__init__()

        self._name_package = name_package
        self._globals = globals
        self._update_globals = update_globals

        self._imps_by_attr: dict[str, _ProxyInit._Import] = {}
        self._mods_by_pkgs: dict[str, ta.Any] = {}

    @property
    def name_package(self) -> NamePackage:
        return self._name_package

    def add(self, package: str, attrs: ta.Iterable[str | tuple[str, str]]) -> None:
        if isinstance(attrs, str):
            raise TypeError(attrs)
        for attr in attrs:
            if isinstance(attr, tuple):
                imp_attr, attr = attr
            else:
                imp_attr = attr
            self._imps_by_attr[attr] = self._Import(package, imp_attr)

    def get(self, attr: str) -> ta.Any:
        try:
            imp = self._imps_by_attr[attr]
        except KeyError:
            raise AttributeError(attr)  # noqa

        try:
            mod = self._mods_by_pkgs[imp.pkg]
        except KeyError:
            mod = importlib.import_module(imp.pkg, package=self._name_package.package)

        val = getattr(mod, imp.attr)

        if self._update_globals and self._globals is not None:
            self._globals[attr] = val

        return val


def proxy_init(
        globals: ta.MutableMapping[str, ta.Any],  # noqa
        package: str,
        attrs: ta.Iterable[str | tuple[str, str]],
) -> None:
    if isinstance(attrs, str):
        raise TypeError(attrs)

    init_name_package = NamePackage(
        globals['__name__'],
        globals['__package__'],
    )

    pi: _ProxyInit
    try:
        pi = globals['__proxy_init__']
    except KeyError:
        pi = _ProxyInit(
            init_name_package,
            globals=globals,
        )
        globals['__proxy_init__'] = pi
        globals['__getattr__'] = pi.get
    else:
        if pi.name_package != init_name_package:
            raise Exception(f'Wrong init name: {pi.name_package=} != {init_name_package=}')

    pi.add(package, attrs)


##


def get_real_module_name(globals: ta.Mapping[str, ta.Any]) -> str:  # noqa
    module = sys.modules[globals['__name__']]

    if module.__spec__ and module.__spec__.name:
        return module.__spec__.name

    if module.__package__:
        return module.__package__

    raise RuntimeError("Can't determine real module name")
