from omlish import dataclasses as dc
from omlish import inject as inj
from omlish import lang

from ...backends.configs import BackendConfig
from ...backends.types import DefaultBackendName
from ..base import Session
from .configs import DEFAULT_BACKEND
from .configs import EmbeddingConfig


with lang.auto_proxy_import(globals()):
    from ...backends import inject as _backends
    from . import session as _session


##


def bind_embedding(cfg: EmbeddingConfig) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.extend([
        inj.bind(_session.EmbeddingSession.Config(**dc.asdict(cfg))),
        inj.bind(Session, to_ctor=_session.EmbeddingSession, singleton=True),
    ])

    #

    els.extend([
        _backends.bind_backends(BackendConfig(
            backend=cfg.backend,
        )),

        inj.bind(DefaultBackendName, to_const=DEFAULT_BACKEND),
    ])

    #

    return inj.as_elements(*els)
