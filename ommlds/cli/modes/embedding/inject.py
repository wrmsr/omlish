from omlish import inject as inj
from omlish import lang

from .... import minichain as mc
from ...backends.configs import BackendConfig
from ...backends.types import DefaultBackendName
from ..base import Mode
from .configs import DEFAULT_BACKEND
from .configs import EmbeddingConfig


with lang.auto_proxy_import(globals()):
    from ...backends import inject as _backends
    from . import mode as _mode


##


def bind_embedding(cfg: EmbeddingConfig) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.extend([
        inj.bind(cfg),
        inj.bind(Mode, to_ctor=_mode.EmbeddingMode, singleton=True),
    ])

    #

    els.extend([
        _backends.bind_backends(
            [
                mc.EmbeddingService,
            ],
            BackendConfig(
                backend=cfg.backend,
            ),
        ),

        inj.bind(DefaultBackendName, to_const=DEFAULT_BACKEND),
    ])

    #

    return inj.as_elements(*els)
