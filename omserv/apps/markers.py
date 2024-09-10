import abc
import typing as ta

from omlish import lang
from omlish.http.asgi import AsgiApp


T = ta.TypeVar('T')


class AppMarker(lang.Abstract):
    pass


APP_MARKERS_ATTR = '__app_markers__'


def append_app_marker(obj: T, *markers: AppMarker) -> T:
    tgt = lang.unwrap_func(obj)  # type: ignore
    tgt.__dict__.setdefault(APP_MARKERS_ATTR, []).extend(markers)
    return obj


def get_app_markers(obj: ta.Any) -> ta.Sequence[AppMarker]:
    tgt = lang.unwrap_func(obj)
    try:
        dct = tgt.__dict__
    except AttributeError:
        return ()
    return dct.get(APP_MARKERS_ATTR, ())


class AppMarkerProcessor(lang.Abstract):
    @abc.abstractmethod
    def __call__(self, app: AsgiApp) -> AsgiApp:
        raise NotImplementedError


class NopAppMarkerProcessor(AppMarkerProcessor, lang.Final):
    def __call__(self, app: AsgiApp) -> AsgiApp:
        return app
