from omlish import inject as inj
from omlish import lang

from .configs import FacadeConfig


with lang.auto_proxy_import(globals()):
    from . import facade as _facade


##


def bind_facade(cfg: FacadeConfig = FacadeConfig()) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.append(inj.bind(_facade.ChatFacade, singleton=True))

    #

    return inj.as_elements(*els)
