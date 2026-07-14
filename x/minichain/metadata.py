import abc
import datetime
import typing as ta
import uuid

from omcore import check
from omcore import dataclasses as dc
from omcore import lang
from omcore import typedvalues as tv

from ._typedvalues import _tv_field_metadata
from .dataclasses import StableDataclass


##


class Metadata(tv.TypedValue, lang.Abstract, lang.PackageSealed):
    pass


MetadataT = ta.TypeVar('MetadataT', bound=Metadata)


#


class MetadataContainer(
    lang.Abstract,
    lang.PackageSealed,
    ta.Generic[MetadataT],
):
    @property
    @abc.abstractmethod
    def metadata(self) -> tv.TypedValues[MetadataT]:
        raise NotImplementedError

    @abc.abstractmethod
    def with_metadata(
            self,
            *add: MetadataT,
            discard: ta.Literal['all'] | ta.Iterable[type] | None = None,
            mode: ta.Literal['append', 'prepend', 'override', 'default'] = 'append',
    ) -> ta.Self:
        raise NotImplementedError


##


@dc.dataclass(frozen=True)
class MetadataContainerDataclass(
    MetadataContainer[MetadataT],
    StableDataclass,
    lang.Abstract,
):
    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        check.state(hasattr(cls, '_metadata'))

    @staticmethod
    def _configure_metadata_field(md_fld, md_cls):
        dc.set_field_metadata(
            check.isinstance(md_fld, dc.Field),
            _tv_field_metadata(
                check.not_none(md_cls),
                marshal_name='metadata',
            ),
        )

    @property
    def metadata(self) -> tv.TypedValues[MetadataT]:
        return check.isinstance(getattr(self, '_metadata'), tv.TypedValues)

    @ta.final
    def with_metadata(
            self,
            *add: MetadataT,
            discard: ta.Literal['all'] | ta.Iterable[type] | None = None,
            mode: ta.Literal['append', 'prepend', 'override', 'default'] = 'append',
    ) -> ta.Self:
        return self.replace(_metadata=self.metadata.update(
            *add,
            discard=discard,
            mode=mode,
        ))


##


class CommonMetadata(Metadata, lang.Abstract, lang.Sealed):
    pass


#


class CreatedAt(tv.UniqueScalarTypedValue[datetime.datetime], CommonMetadata, lang.Final):
    pass


#


class RequestUuid(tv.UniqueScalarTypedValue[uuid.UUID], CommonMetadata, lang.Final):
    pass


class ParentRequestUuid(tv.UniqueScalarTypedValue[uuid.UUID], CommonMetadata, lang.Final):
    pass


class ResponseUuid(tv.UniqueScalarTypedValue[uuid.UUID], CommonMetadata, lang.Final):
    pass
