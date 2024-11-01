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
import typing as ta

from omlish import lang


class _ProxyInit:
    def __init__(
            self,
            name: str,
            *,
            globals: ta.MutableMapping[str, ta.Any] | None = None,  # noqa
            update_globals: bool = False,
    ) -> None:
        super().__init__()

        self._name = name
        self._globals = globals
        self._update_globals = update_globals

        self._pkgs_by_attr: dict[str, str] = {}

    @property
    def name(self) -> str:
        return self._name

    def add(self, package, attrs: ta.Iterable[str]) -> None:
        if isinstance(attrs, str):
            raise TypeError(attrs)
        for attr in attrs:
            self._pkgs_by_attr[attr] = package

    def get(self, attr: str) -> ta.Any:
        return 'barf'


def proxy_init(
        globals: ta.MutableMapping[str, ta.Any],  # noqa
        package: str,
        attrs: ta.Iterable[str],
) -> None:
    if isinstance(attrs, str):
        raise TypeError(attrs)

    init_name = globals['__name__']

    pi: _ProxyInit
    try:
        pi = globals['__proxy_init__']
    except KeyError:
        pi = _ProxyInit(
            init_name,
            globals=globals,
        )
        globals['__proxy_init__'] = pi
        globals['__getattr__'] = pi.get
    else:
        if pi.name != init_name:
            raise Exception(f'Wrong init name: {pi.name=} != {init_name=}')


def _main() -> None:
    from . import proxy_init_test as pit
    print(pit)
    print(pit._ta)
    print(pit.foo)
    print(pit.foo)


if __name__ == '__main__':
    _main()
