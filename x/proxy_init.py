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


def proxy_init(
        globals: ta.MutableMapping[str, ta.Any],  # noqa
        package: str,
        attrs: ta.Sequence[str],
) -> None:
    if isinstance(attrs, str):
        raise TypeError(attrs)

    raise NotImplementedError


def _main() -> None:
    pass


if __name__ == '__main__':
    _main()
