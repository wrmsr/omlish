from omlish import inject as inj
from omserv.apps.inject import bind_handler

from .auth import AuthHandler
from .diag import DiagHandler
from .favicon import FaviconHandler
from .index import IndexHandler
from .login import LoginHandler
from .logout import LogoutHandler
from .profile import ProfileHandler
from .sd import SdHandler
from .signup import SignupHandler
from .tik import TikHandler


def bind() -> inj.Elemental:
    return inj.as_elements(
        bind_handler(AuthHandler),
        bind_handler(DiagHandler),
        bind_handler(FaviconHandler),
        bind_handler(IndexHandler),
        bind_handler(LoginHandler),
        bind_handler(LogoutHandler),
        bind_handler(ProfileHandler),
        bind_handler(SdHandler),
        bind_handler(SignupHandler),
        bind_handler(TikHandler),
    )
