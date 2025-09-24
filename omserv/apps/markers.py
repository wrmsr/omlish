import abc
import typing as ta

from omlish import lang
from omlish.http import asgi
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
    return get_object_metadata(obj, type=AppMarker)


##


class AppMarkerProcessor(lang.Abstract):
    @abc.abstractmethod
    def process_app(self, app: asgi.App) -> asgi.App:
        raise NotImplementedError


class NopAppMarkerProcessor(AppMarkerProcessor, lang.Final):
    def process_app(self, app: asgi.App) -> asgi.App:
        return app


##


AppMarkerProcessorMap: ta.TypeAlias = ta.Mapping[type[AppMarker], AppMarkerProcessor]
