"""
if _ta.TYPE_CHECKING:
    from .skiplist import (  # noqa
        SkipList,
        SkipListDict,
    )
else:
    lang.proxy_init(globals(), '.skiplist', [
        'SkipList',
        'SkipListDict',
    ])
"""
import importlib
import typing as ta

from omlish import lang


class NamePackage(ta.NamedTuple):
    name: str
    package: str


class _ProxyInit:
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

        self._pkgs_by_attr: dict[str, str] = {}
        self._mods_by_pkgs: dict[str, ta.Any] = {}

    @property
    def name_package(self) -> NamePackage:
        return self._name_package

    def add(self, package: str, attrs: ta.Iterable[str]) -> None:
        if isinstance(attrs, str):
            raise TypeError(attrs)
        for attr in attrs:
            self._pkgs_by_attr[attr] = package

    def get(self, attr: str) -> ta.Any:
        try:
            pkg = self._pkgs_by_attr[attr]
        except KeyError:
            raise AttributeError(attr)

        try:
            mod = self._mods_by_pkgs[pkg]
        except KeyError:
            mod = importlib.import_module(pkg, package=self.name_package.package)


def proxy_init(
        globals: ta.MutableMapping[str, ta.Any],  # noqa
        package: str,
        attrs: ta.Iterable[str],
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


def _main() -> None:
    from . import proxy_init_test as pit
    print(pit)
    print(pit._ta)
    print(pit.foo)
    print(pit.foo)


if __name__ == '__main__':
    _main()
