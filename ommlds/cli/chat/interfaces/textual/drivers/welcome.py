import os

from ...... import minichain as mc
from .....types import ProfileName
from ....backends.types import BackendSpecGetter
from ..widgets.messages.welcome import WelcomeMessage


##


def _render_backend_spec(spec: mc.BackendSpec) -> str:
    # Specs may legitimately carry in-process-only configs (ConfigBackendSpec takes ta.Any) - display must not die
    # on them.
    try:
        return spec.as_json()
    except Exception:  # noqa
        return repr(spec)


async def build_welcome_message(
        *,
        backend: BackendSpecGetter | None = None,
        entrypoint_profile_name: ProfileName | None = None,
        driver_id: mc.drivers.DriverId,
        chat_id: mc.drivers.ChatId,
        chat_manager: mc.drivers.DriverStorageManager,
) -> WelcomeMessage:
    chat = await chat_manager.get_chat()

    return WelcomeMessage(
        '\n'.join([
            *([f'Profile: {entrypoint_profile_name}'] if entrypoint_profile_name is not None else []),
            f'Chat Id: {chat_id.v}',
            f'Chat Length: {len(chat)}',
            f'Driver Id: {driver_id.v}',
            f'Backend: {_render_backend_spec(await backend()) if backend is not None else "?"}',
            f'Working Dir: {os.getcwd()}',
        ]),
        copy_contents={
            'chat_id': ('Chat Id', str(chat_id.v)),
            'driver_id': ('Driver Id', str(driver_id.v)),
        },
    )
