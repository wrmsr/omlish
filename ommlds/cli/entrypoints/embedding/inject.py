from omlish import inject as inj
from omlish import lang

from .... import minichain as mc
from ...backends.configs import BackendConfig
from ...backends.types import DefaultBackendName
from ..base import Entrypoint
from .configs import DEFAULT_BACKEND
from .configs import EmbeddingConfig


with lang.auto_proxy_import(globals()):
    from ...backends import inject as _backends
    from . import entrypoint as _entrypoint


##


def bind_embedding(cfg: EmbeddingConfig) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.extend([
        inj.bind(cfg),
        inj.bind(Entrypoint, to_ctor=_entrypoint.EmbeddingEntrypoint, singleton=True),
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
