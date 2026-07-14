from .. import lang as _lang


with _lang.auto_proxy_init(globals()):
    ##

    from .dispatch import (  # noqa
        Dispatcher,
    )

    from .functions import (  # noqa
        function,
    )

    from .methods import (  # noqa
        install_method,
        method,
    )
