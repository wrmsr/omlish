import threading
import typing as ta

from ... import lang
from ._compat import compat
from .app import App
from .cvs import Cvs
from .requests import Request
from .responses import Response


##


class Api:
    def __init__(
            self,
            *,
            base_app_cls: type[App] = App,
    ) -> None:
        super().__init__()

        self._base_app_cls = base_app_cls

        self._lock = threading.RLock()

    @property
    def _cls_name_repr(self) -> str:
        return f'{self.__class__.__name__}@{id(self):x}'

    def __repr__(self) -> str:
        return f'{self._cls_name_repr}()'

    ##
    # app cls

    _app_cls: type[App]

    @property
    def app_cls(self) -> type[App]:
        try:
            return self._app_cls
        except AttributeError:
            pass

        with self._lock:
            try:
                return self._app_cls
            except AttributeError:
                pass

            self._app_cls = lang.new_type(  # noqa
                f'{self._base_app_cls.__name__}<{self._cls_name_repr}>',
                (self._base_app_cls,),
                {'_api': self},
            )

            return self._app_cls

    @property
    @compat
    def Flask(self) -> type[App]:  # noqa
        return self.app_cls

    ##
    # helpers

    def abort(self, code: int | Response, *args: ta.Any, **kwargs: ta.Any) -> ta.NoReturn:
        raise NotImplementedError

    ##
    # cv's

    @property
    @compat
    def request(self) -> Request:
        return Cvs.REQUEST.get()

    ##
    # type aliases - must be last

    Response = Response
