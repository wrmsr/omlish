"""
FIXME:
 - too lazy to lazy import guts like every other proper inject module lol >_<
"""
import asyncio

from omlish import inject as inj

from ...drivers.events.injection import event_callbacks
from ..base import ChatInterface
from .app import ChatApp
from .app import ChatDriverEventQueue
from .interface import TextualChatInterface


##


def bind_textual() -> inj.Elements:
    els: list[inj.Elemental] = [
        inj.bind(ChatInterface, to_ctor=TextualChatInterface, singleton=True),
    ]

    #

    els.extend([
        inj.bind(ChatApp, singleton=True),
    ])

    #

    els.extend([
        inj.bind(ChatDriverEventQueue, to_const=asyncio.Queue()),

        event_callbacks().bind_item(to_fn=inj.KwargsTarget.of(
            lambda eq: lambda ev: eq.put(ev),
            eq=ChatDriverEventQueue,
        )),
    ])

    #

    return inj.as_elements(*els)
