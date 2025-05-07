from omlish import inject as inj

from ..sessions.inject import bind_chat_options
from .tools import WEATHER_TOOL


##


def bind_tools() -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.append(bind_chat_options(
        WEATHER_TOOL,
    ))

    #

    return inj.as_elements(*els)
