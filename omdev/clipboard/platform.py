import platform

from omlish import lang

from .commands import PbcopyDarwinClipboard
from .commands import XclipLinuxClipboard
from .types import Clipboard


##


@lang.cached_function
def get_platform_clipboard() -> Clipboard | None:
    match platform.system():
        case 'Darwin':
            return PbcopyDarwinClipboard()
        case 'Linux':
            return XclipLinuxClipboard()
        case _:
            return None
