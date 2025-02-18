import abc
import typing as ta

from omlish import lang
from omlish.http.asgi import AsgiApp
from omlish.metadata import ObjectMetadata
from omlish.metadata import append_object_metadata
from omlish.metadata import get_object_metadata


T = ta.TypeVar('T')


##


class AppMarker(ObjectMetadata, lang.Abstract):
    pass


##


def append_app_marker(obj: T, *markers: AppMarker) -> T:
    append_object_metadata(obj, *markers)
    return obj


def get_app_markers(obj: ta.Any) -> ta.Sequence[AppMarker]:
    return [md for md in get_object_metadata(obj) if isinstance(md, AppMarker)]


##


class AppMarkerProcessor(lang.Abstract):
    @abc.abstractmethod
    def __call__(self, app: AsgiApp) -> AsgiApp:
        raise NotImplementedError


class NopAppMarkerProcessor(AppMarkerProcessor, lang.Final):
    def __call__(self, app: AsgiApp) -> AsgiApp:
        return app
