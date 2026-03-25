import os

from ...... import minichain as mc
from .....backends.types import BackendName
from ....types import ProfileName
from .widgets.messages import WelcomeMessage


##


def build_welcome_message(
        *,
        backend_name: BackendName | None = None,
        mode_profile_name: ProfileName | None = None,
        driver_id: mc.drivers.DriverId,
) -> WelcomeMessage:
    return WelcomeMessage('\n'.join([
        *([f'Profile: {mode_profile_name}'] if mode_profile_name is not None else []),
        f'Driver Id: {driver_id.v}',
        f'Backend: {backend_name or "?"}',
        f'Working Dir: {os.getcwd()}',
    ]))
