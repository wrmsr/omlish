"""
TODO:
 - proxy_init 'as' alias support - attrs of (src, dst)
"""
import functools
import importlib.util
import typing as ta

from ..lazyglobals import LazyGlobals


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

    def add(self, package: str, attrs: ta.Iterable[str | tuple[str, str]]) -> None:
        if isinstance(attrs, str):
            raise TypeError(attrs)

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

        try:
            mod = self._mods_by_pkgs[imp.pkg]
        except KeyError:
            mod = importlib.import_module(imp.pkg, package=self._name_package.package)

        val = getattr(mod, imp.attr)

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
            LazyGlobals.install(globals),
            init_name_package,
        )
        globals['__proxy_init__'] = pi

    else:
        if pi.name_package != init_name_package:
            raise Exception(f'Wrong init name: {pi.name_package=} != {init_name_package=}')

    pi.add(package, attrs)
