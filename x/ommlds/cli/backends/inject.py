import functools
import typing as ta

from omlish import inject as inj
from omlish import lang

from ... import minichain as mc
from .configs import BackendConfig
from .injection import backend_configs


with lang.auto_proxy_import(globals()):
    from . import types as _types


##


def bind_backends(
        service_cls_lst: ta.Sequence[ta.Any],
        /,
        cfg: BackendConfig = BackendConfig(),
) -> inj.Elements:
    lst: list[inj.Elemental] = []

    #

    lst.append(backend_configs().bind_items_provider(singleton=True))

    #

    if cfg.backend is not None:
        lst.append(inj.bind(_types.BackendName, to_const=cfg.backend))
    else:
        lst.append(inj.bind(_types.BackendName, to_fn=inj.target(dbn=_types.DefaultBackendName)(lambda dbn: dbn)))

    service_cls: ta.Any
    for service_cls in service_cls_lst:
        lst.append(
            inj.bind(
                mc.ServiceProvider[service_cls],  # noqa
                to_fn=inj.target(
                    spec=_types.BackendName,
                    configs=_types.BackendConfigs,
                )(functools.partial(
                    mc.BackendSpecServiceProvider,
                    service_cls,
                )),
                singleton=True,
            ),
        )

    #

    return inj.as_elements(*lst)
