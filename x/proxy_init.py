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
    def __init__(self, package: str) -> None:
        super().__init__()

        self._package = package

    @property
    def package(self) -> str:
        return self._package

    def get(self, attr: str) -> ta.Any:
        raise NotImplementedError


def proxy_init(
        globals: ta.MutableMapping[str, ta.Any],  # noqa
        package: str,
        attrs: ta.Sequence[str],
) -> None:
    if isinstance(attrs, str):
        raise TypeError(attrs)

    init_package = globals['__name__']

    pi: _ProxyInit
    try:
        pi = globals['__proxy_init__']
    except KeyError:
        pi = _ProxyInit(init_package)
        globals['__proxy_init__'] = pi
    else:
        if pi.package != init_package:
            raise Exception('Wrong init package')


def _main() -> None:
    from . import proxy_init_test as pit
    print(pit)
    print(pit._ta)
    print(pit.foo)


if __name__ == '__main__':
    _main()
