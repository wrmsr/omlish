from omlish import dataclasses as dc
from omlish import inject as inj
from omlish import lang

from ..base import Session
from .configs import ChatConfig


with lang.auto_proxy_import(globals()):
    from ...rendering import inject as _rendering
    from . import session as _session
    from .drivers import inject as _drivers
    from .interfaces import inject as _interfaces


##


def bind_chat(cfg: ChatConfig) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.extend([
        _drivers.bind_driver(cfg.driver),

        _interfaces.bind_interface(cfg.interface),

        _rendering.bind_rendering(cfg.rendering),
    ])

    #

    els.extend([
        inj.bind(_session.ChatSession.Config(**dc.asdict(cfg))),
        inj.bind(Session, to_ctor=_session.ChatSession, singleton=True),
    ])

    #

    return inj.as_elements(*els)
