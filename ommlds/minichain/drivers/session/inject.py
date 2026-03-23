from omlish import inject as inj

from .configs import SessionConfig


##


def bind_session(cfg: SessionConfig = SessionConfig()) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    return inj.as_elements(*els)
