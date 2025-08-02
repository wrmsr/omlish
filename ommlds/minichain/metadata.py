import abc
import datetime
import typing as ta
import uuid

from omlish import lang
from omlish import typedvalues as tv


##


class Metadata(tv.TypedValue, lang.Abstract, lang.PackageSealed):
    pass


MetadataT = ta.TypeVar('MetadataT', bound=Metadata)


#


class MetadataContainer(
    tv.TypedValueGeneric[MetadataT],
    lang.Abstract,
    lang.PackageSealed,
):
    @property
    @abc.abstractmethod
    def metadata(self) -> tv.TypedValues[MetadataT]:
        raise NotImplementedError

    @abc.abstractmethod
    def with_metadata(self, *mds: MetadataT, override: bool = False) -> ta.Self:
        raise NotImplementedError


##


class CommonMetadata(Metadata, lang.Abstract):
    pass


class Uuid(tv.ScalarTypedValue[uuid.UUID], CommonMetadata, lang.Final):
    pass


class CreatedAt(tv.ScalarTypedValue[datetime.datetime], CommonMetadata, lang.Final):
    pass
