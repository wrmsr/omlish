import os

from ...... import minichain as mc
from ....types import ProfileName
from ...backends.types import BackendSpecGetter
from .widgets.messages import WelcomeMessage


##


async def build_welcome_message(
        *,
        backend: BackendSpecGetter | None = None,
        mode_profile_name: ProfileName | None = None,
        driver_id: mc.drivers.DriverId,
        chat_id: mc.drivers.ChatId,
        chat_manager: mc.drivers.DriverStateManager,
) -> WelcomeMessage:
    chat = await chat_manager.get_chat()

    return WelcomeMessage('\n'.join([
        *([f'Profile: {mode_profile_name}'] if mode_profile_name is not None else []),
        f'Chat Id: {chat_id.v}',
        f'Chat Length: {len(chat)}',
        f'Driver Id: {driver_id.v}',
        f'Backend: {(await backend()).as_json() if backend is not None else "?"}',
        f'Working Dir: {os.getcwd()}',
    ]))
