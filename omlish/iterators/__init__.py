from .. import lang as _lang  # noqa


with _lang.auto_proxy_init(globals()):
    ##

    from .iterators import (  # noqa
        PeekIterator,
        PrefetchIterator,
        ProxyIterator,
        RetainIterator,
    )

    from .recipes import (  # noqa
        sliding_window,
    )

    from .tools import (  # noqa
        expand_indexed_pairs,
        merge_on,
        take,
        unzip,
    )

    from . import transforms as tf  # noqa

    from .unique import (  # noqa
        UniqueItem,
        UniqueIterator,
        UniqueStats,
    )
