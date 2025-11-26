from .errors import (  # noqa
    KnownError,
    KnownErrors,

    CUSTOM_ERROR_BASE,
)

from .types import (  # noqa
    NUMBER_TYPES,
    Number,
    Object,
    ID_TYPES,
    Id,

    VERSION,

    NotSpecified,
    is_not_specified,
    check_not_not_specified,

    Request,
    request,
    notification,

    Response,
    result,

    Error,
    error,

    Message,
    detect_message_type,
)


##


from ... import lang as _lang


with _lang.auto_proxy_init(globals()):
    from .conns import (  # noqa
        JsonrpcConnection as Connection,
    )


##


from ... import marshal as _msh


_msh.register_global_module_import('._marshal', __package__)
