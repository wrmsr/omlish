from omlish import inject as inj

from .simple import SimpleChatPreparer
from .types import ChatPreparer


##


def bind_preparing() -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.append(inj.bind(ChatPreparer, to_ctor=SimpleChatPreparer, singleton=True))

    #

    return inj.as_elements(*els)
