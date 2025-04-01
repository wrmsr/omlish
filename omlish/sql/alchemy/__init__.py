# ruff: noqa: I001
import typing as _ta

from ... import lang as _lang


if _ta.TYPE_CHECKING:
    from .apiadapter import (  # noqa
        SqlalchemyApiWrapper,

        SqlalchemyApiRows,
        SqlalchemyApiConn,
        SqlalchemyApiDb,
        SqlalchemyApiAdapter,

        api_adapt,
    )

else:
    _lang.proxy_init(globals(), '.apiadapter', [
        'SqlalchemyApiWrapper',

        'SqlalchemyApiRows',
        'SqlalchemyApiConn',
        'SqlalchemyApiDb',
        'SqlalchemyApiAdapter',

        'api_adapt',
    ])


from .asyncs import (  # noqa
    AsyncConnection,
    AsyncConnectionLike,
    AsyncEngine,
    AsyncEngineLike,
    AsyncTransaction,
    AsyncTransactionLike,
    async_adapt,
)

from .exprs import (  # noqa
    paren,
)
