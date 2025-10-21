from omlish import dataclasses as dc
from omlish import inject as inj
from omlish import lang

from ..base import Session
from .configs import EmbeddingConfig


with lang.auto_proxy_import(globals()):
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

    return inj.as_elements(*els)
