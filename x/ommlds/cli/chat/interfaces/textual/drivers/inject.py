from omcore import inject as inj
from omcore import lang

from ....configs import ChatConfig
from .types import ChatDriverInterfaceGetter


with lang.auto_proxy_import(globals()):
    from . import manager as _manager


##


def bind_driver(
        *,
        chat_cfg: ChatConfig = ChatConfig(),
) -> inj.Elements:
    return inj.as_elements(
        inj.bind(
            _manager.DriverManager,
            to_async_fn=inj.make_async_managed_provider(_manager.DriverManager),
            singleton=True,
        ),

        inj.bind(ChatConfig, to_const=chat_cfg),

        inj.bind(
            ChatDriverInterfaceGetter,
            to_fn=inj.target(
                dm=_manager.DriverManager,
            )(lambda dm: ChatDriverInterfaceGetter(dm.get_chat_driver_interface)),
            singleton=True,
        ),
    )
