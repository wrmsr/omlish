from omlish import inject as inj

from .....apps.inject import bind_route_handler_class
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


##


def bind() -> inj.Elemental:
    return inj.as_elements(
        bind_route_handler_class(AuthHandler),
        bind_route_handler_class(DiagHandler),
        bind_route_handler_class(FaviconHandler),
        bind_route_handler_class(IndexHandler),
        bind_route_handler_class(LoginHandler),
        bind_route_handler_class(LogoutHandler),
        bind_route_handler_class(ProfileHandler),
        bind_route_handler_class(SdHandler),
        bind_route_handler_class(SignupHandler),
        bind_route_handler_class(TikHandler),
    )
